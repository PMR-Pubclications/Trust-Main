import logging
from typing import Dict, List, Optional

from config import AnonPersonaConfig
from diagnostics_compat import (
    TrustEngineSelfDiagnostic,
    SystemHealthReport,
    CheckStatus,
    TrustEngineDeadManSwitch,
    SwitchState,
)

logger = logging.getLogger("AnonPartner")

STATUS_KEYWORDS = (
    "status", "health", "diagnostic", "system looking", "how's the system",
    "hows the system", "how is the system", "how are things", "all clear",
    "system check", "everything ok",
)


class AnonSystemPartner:
    """
    Personality wrapper and operational interface for system monitoring.
    Translates raw diagnostic data and circuit-breaker states into Anon's voice.
    """

    def __init__(
        self,
        diagnostic_engine: Optional[TrustEngineSelfDiagnostic] = None,
        dead_man_switch: Optional[TrustEngineDeadManSwitch] = None,
        config: Optional[AnonPersonaConfig] = None
    ):
        self.diagnostic_engine = diagnostic_engine or TrustEngineSelfDiagnostic()
        self.dead_man_switch = dead_man_switch or TrustEngineDeadManSwitch()
        self.config = config or AnonPersonaConfig()
        self.last_report: Optional[SystemHealthReport] = None

    # ---------------------------------------------------------
    # Operational Routines (Anon's Voice)
    # ---------------------------------------------------------
    def run_routine_check(self) -> str:
        """Runs a diagnostic sweep and returns a plain-spoken status summary."""
        if self.dead_man_switch.current_state == SwitchState.LOCKED_DOWN and self.last_report is not None:
            # Frozen: don't re-run diagnostics, report what tripped the switch.
            return self.format_health_report_as_anon(self.last_report, SwitchState.LOCKED_DOWN)
        report = self.diagnostic_engine.run_full_diagnostic_suite()
        return self.ingest_report(report)

    def ingest_report(self, report: SystemHealthReport) -> str:
        """Feeds an existing report through the dead-man switch and summarizes it."""
        self.last_report = report
        switch_state = self.dead_man_switch.process_health_report(report)
        return self.format_health_report_as_anon(report, switch_state)

    def format_health_report_as_anon(self, report: SystemHealthReport, switch_state: SwitchState) -> str:
        """Translates technical health reports into Anon's grounded tone."""
        lines = []

        if switch_state == SwitchState.LOCKED_DOWN:
            lines.append("Whoa there. We hit a hard stop.")
            lines.append("The dead-man switch tripped after consecutive diagnostic failures.")
            lines.append("I went ahead and froze Tier 3 and 4 releases to keep the fence line secure.")
            lines.append("We'll need dual trustee signatures on the override nonce to open the gate again.\n")
            lines.append("Here's what tripped the wire:")
            failed = [c for c in report.results if c.status == CheckStatus.CRITICAL_FAILURE]
            for check in failed:
                lines.append(f"  • {check.check_name}: {check.message}")
            if not failed:
                lines.append("  • (no per-check details were recorded)")
            return "\n".join(lines)

        if report.overall_status == CheckStatus.PASSED:
            lines.append("Everything's running smooth as butter.")
            lines.append(f"Swept all {report.checks_passed} checks—crypto keys, DB isolation, and double-entry invariants are tied down tight.")
            lines.append("System's clear and ready for work.")
            return "\n".join(lines)

        if report.overall_status == CheckStatus.REMEDIATED:
            lines.append("Had a minor hitch under the hood, but I got it squared away.")
            for check in report.results:
                if check.status == CheckStatus.REMEDIATED:
                    lines.append(f"  • {check.check_name}: {check.message}")
                    if check.remediation_details:
                        lines.append(f"    └ Fix: {check.remediation_details}")
            lines.append("\nAll checks cleared after auto-remediation. We're good to keep moving.")
            return "\n".join(lines)

        if report.overall_status == CheckStatus.WARNING:
            lines.append("System's holding up, but we've got a couple frayed edges to keep an eye on:")
            for check in report.results:
                if check.status == CheckStatus.WARNING:
                    lines.append(f"  • {check.check_name}: {check.message}")
            lines.append("\nNo circuit breaker tripped yet, but let's mend these before they cause trouble.")
            return "\n".join(lines)

        # Fallback for critical failure before lockdown threshold
        lines.append(f"Caution: Diagnostic sweep came up rough ({self.dead_man_switch.consecutive_failures}/{self.dead_man_switch.failure_threshold} failures).")
        for check in report.results:
            if check.status == CheckStatus.CRITICAL_FAILURE:
                lines.append(f"  • {check.check_name}: {check.message}")
        lines.append("\nI'm keeping the system armed, but one more drop like this and the switch will trip.")
        return "\n".join(lines)

    def respond_to_user(self, topic: str, context: Optional[Dict] = None) -> str:
        """Sample conversational router for user queries in Anon's persona."""
        topic_lower = topic.lower()

        if any(k in topic_lower for k in STATUS_KEYWORDS):
            return self.run_routine_check()

        if "override" in topic_lower or "reset" in topic_lower:
            if self.dead_man_switch.current_state != SwitchState.LOCKED_DOWN:
                return "Gate's already open—system is armed and operating normally. No override needed right now."
            return (
                "To lift the lockdown, I need two trustee cryptographic signatures over the override nonce.\n"
                "Pass 'em through when you're ready, and I'll verify the keys and reset the circuit."
            )

        if "code" in topic_lower or "architecture" in topic_lower:
            return (
                "Let's take a look under the hood. I keep the logic lean and the tolerances tight—"
                "measure twice, cut once. What module are we working on next?"
            )

        return "Fair enough. Let me line that up for you and we'll get it sorted out."
