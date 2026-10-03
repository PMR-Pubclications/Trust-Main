import os
import json
import logging
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct

# Imports from previous diagnostic modules
from trust_system_diagnostics_remediated import CheckStatus, SystemHealthReport

logger = logging.getLogger("DeadManSwitch")


class SwitchState(str, Enum):
    ARMED = "ARMED"              # Normal operation; monitoring diagnostics
    WARNING = "WARNING"          # 1 or 2 consecutive failures recorded
    LOCKED_DOWN = "LOCKED_DOWN"  # Threshold exceeded; all state transitions frozen


class LockdownAuditEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger_reason: str
    consecutive_failures: int
    last_failed_checks: List[str]


class TrustEngineDeadManSwitch:
    """
    Stateful circuit breaker that tracks diagnostic health reports and enforces
    system-wide lockdown upon 3 consecutive critical diagnostic failures.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        state_file_path: str = "/tmp/trust_dead_man_switch_state.json",
        authorized_trustee_keys: Optional[List[str]] = None
    ):
        self.failure_threshold = failure_threshold
        self.state_file_path = state_file_path
        self.authorized_trustee_keys = [k.lower() for k in (authorized_trustee_keys or [])]
        
        # Internal state variables
        self.consecutive_failures: int = 0
        self.current_state: SwitchState = SwitchState.ARMED
        self.lockdown_event: Optional[LockdownAuditEvent] = None
        
        # Hydrate state from persistent file on startup
        self._load_state()

    # ---------------------------------------------------------
    # Core Health Assessment & State Engine
    # ---------------------------------------------------------
    def process_health_report(self, report: SystemHealthReport) -> SwitchState:
        """
        Evaluates incoming health report, updates failure counters, and
        triggers lockdown if failure threshold is reached.
        """
        if self.current_state == SwitchState.LOCKED_DOWN:
            logger.critical("System is LOCKED DOWN. Ignoring health report execution.")
            return SwitchState.LOCKED_DOWN

        if report.overall_status == CheckStatus.CRITICAL_FAILURE:
            self.consecutive_failures += 1
            failed_check_names = [
                c.check_name for c in report.results 
                if c.status == CheckStatus.CRITICAL_FAILURE
            ]
            
            logger.warning(
                f"Diagnostic failure recorded ({self.consecutive_failures}/{self.failure_threshold}). "
                f"Failed checks: {failed_check_names}"
            )

            if self.consecutive_failures >= self.failure_threshold:
                self._execute_lockdown(
                    reason=f"Reached {self.consecutive_failures} consecutive diagnostic failures.",
                    failed_checks=failed_check_names
                )
            else:
                self.current_state = SwitchState.WARNING
                self._persist_state()

        else:
            # Any non-critical status (PASSED, REMEDIATED, WARNING) resets the counter
            if self.consecutive_failures > 0:
                logger.info(f"System recovered. Consecutive failure counter reset from {self.consecutive_failures} to 0.")
            self.consecutive_failures = 0
            self.current_state = SwitchState.ARMED
            self._persist_state()

        return self.current_state

    def is_execution_allowed(self) -> bool:
        """Returns True only if the switch is in ARMED or WARNING state."""
        return self.current_state != SwitchState.LOCKED_DOWN

    # ---------------------------------------------------------
    # Lockdown Enforcement Routine
    # ---------------------------------------------------------
    def _execute_lockdown(self, reason: str, failed_checks: List[str]):
        """Executes emergency lockdown: updates state, persists lockfile, and isolates system."""
        self.current_state = SwitchState.LOCKED_DOWN
        self.lockdown_event = LockdownAuditEvent(
            trigger_reason=reason,
            consecutive_failures=self.consecutive_failures,
            last_failed_checks=failed_checks
        )
        self._persist_state()

        # Operational Isolation Actions
        logger.critical("=====================================================")
        logger.critical("!!! EMERGENCY SYSTEM LOCKDOWN TRIGGERED !!!")
        logger.critical(f"Reason: {reason}")
        logger.critical(f"Failed Checks: {failed_checks}")
        logger.critical("Actions Enforced:")
        logger.critical("  1. Tier 3/4 Disbursement Execution API Frozen.")
        logger.critical("  2. Database connections scoped to READ-ONLY.")
        logger.critical("  3. Dual-trustee cryptographic clearance required to reset.")
        logger.critical("=====================================================")

    # ---------------------------------------------------------
    # Cryptographic Emergency Manual Recovery
    # ---------------------------------------------------------
    def manual_override_reset(self, signatures: List[Dict[str, str]], override_nonce: str) -> bool:
        """
        Requires 2 valid trustee signatures over the override nonce to clear lockdown state.
        signatures format: [{"address": "0x...", "signature": "0x..."}, ...]
        """
        if self.current_state != SwitchState.LOCKED_DOWN:
            logger.info("Override attempt ignored: System is not in LOCKED_DOWN state.")
            return True

        if len(signatures) < 2:
            logger.error("Override failed: Dual signatures required (minimum 2).")
            return False

        message_bytes = f"EMERGENCY_LOCKDOWN_OVERRIDE:{override_nonce}".encode('utf-8')
        encoded_msg = encode_defunct(primitive=message_bytes)
        verified_addresses = set()

        for sig_item in signatures:
            try:
                addr = EthAccount.recover_message(encoded_msg, signature=sig_item["signature"]).lower()
                if addr in self.authorized_trustee_keys:
                    verified_addresses.add(addr)
            except Exception as e:
                logger.error(f"Signature verification error: {str(e)}")

        if len(verified_addresses) >= 2:
            logger.info(f"Lockdown override authorized by trustees: {list(verified_addresses)}")
            self.consecutive_failures = 0
            self.current_state = SwitchState.ARMED
            self.lockdown_event = None
            self._persist_state()
            return True
        else:
            logger.error(f"Override failed: Valid trustee signatures count ({len(verified_addresses)}) < 2.")
            return False

    # ---------------------------------------------------------
    # Persistence Helpers
    # ---------------------------------------------------------
    def _persist_state(self):
        """Atomically persists switch state to disk to prevent state reset on process restart."""
        payload = {
            "current_state": self.current_state.value,
            "consecutive_failures": self.consecutive_failures,
            "lockdown_event": self.lockdown_event.model_dump(mode="json") if self.lockdown_event else None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        temp_path = f"{self.state_file_path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(payload, f, indent=2)
        os.replace(temp_path, self.state_file_path)

    def _load_state(self):
        """Hydrates state from disk on application startup."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r") as f:
                    data = json.load(f)
                    self.current_state = SwitchState(data["current_state"])
                    self.consecutive_failures = data["consecutive_failures"]
                    if data.get("lockdown_event"):
                        self.lockdown_event = LockdownAuditEvent(**data["lockdown_event"])
            except Exception as e:
                logger.error(f"Failed to load switch state from file; initializing defaults. Error: {str(e)}")
