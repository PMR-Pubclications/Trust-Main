"""
Imports the real diagnostics / dead-man-switch modules from the parent
legacyTrust-AI folder. If their heavy dependencies (pydantic, eth_account,
psycopg, ...) are unavailable, minimal local stand-ins with the same
interface are used so the persona can still run and be tested.
`USING_STUBS` tells callers which one is active.
"""
import config  # noqa: F401  (sets up sys.path)

try:
    from trust_system_diagnostics_remediated import (
        TrustEngineSelfDiagnostic, SystemHealthReport, CheckStatus,
        DiagnosticCheckResult,
    )
    from trust_dead_man_switch import TrustEngineDeadManSwitch, SwitchState
    USING_STUBS = False
except ImportError:
    USING_STUBS = True
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import List, Optional

    class CheckStatus(str, Enum):
        PASSED = "PASSED"
        REMEDIATED = "REMEDIATED"
        WARNING = "WARNING"
        CRITICAL_FAILURE = "CRITICAL_FAILURE"

    class SwitchState(str, Enum):
        ARMED = "ARMED"
        WARNING = "WARNING"
        LOCKED_DOWN = "LOCKED_DOWN"

    @dataclass
    class DiagnosticCheckResult:
        check_name: str
        category: str
        status: CheckStatus
        latency_ms: float
        message: str = ""
        remediation_details: Optional[str] = None

    @dataclass
    class SystemHealthReport:
        overall_status: CheckStatus
        checks_passed: int = 0
        checks_remediated: int = 0
        checks_warned: int = 0
        checks_failed: int = 0
        results: List[DiagnosticCheckResult] = field(default_factory=list)

    class TrustEngineSelfDiagnostic:
        """Stub: reports a clean sweep."""

        def run_full_diagnostic_suite(self) -> SystemHealthReport:
            return SystemHealthReport(overall_status=CheckStatus.PASSED, checks_passed=6)

    class TrustEngineDeadManSwitch:
        """Stub: in-memory circuit breaker (no persistence or signatures)."""

        def __init__(self, failure_threshold: int = 3, **_):
            self.failure_threshold = failure_threshold
            self.consecutive_failures = 0
            self.current_state = SwitchState.ARMED

        def process_health_report(self, report) -> SwitchState:
            if self.current_state == SwitchState.LOCKED_DOWN:
                return self.current_state
            if report.overall_status == CheckStatus.CRITICAL_FAILURE:
                self.consecutive_failures += 1
                self.current_state = (
                    SwitchState.LOCKED_DOWN
                    if self.consecutive_failures >= self.failure_threshold
                    else SwitchState.WARNING
                )
            else:
                self.consecutive_failures = 0
                self.current_state = SwitchState.ARMED
            return self.current_state
