"""Persona test harness. Run with `python test_persona.py` or `pytest`."""
from anon_system_partner import AnonSystemPartner
from diagnostics_compat import (
    CheckStatus, SwitchState, SystemHealthReport, DiagnosticCheckResult,
    TrustEngineSelfDiagnostic, TrustEngineDeadManSwitch,
)


class _PassingDiagnostics:
    def run_full_diagnostic_suite(self):
        return SystemHealthReport(
            overall_status=CheckStatus.PASSED, checks_passed=6, checks_remediated=0,
            checks_warned=0, checks_failed=0, results=[],
        )


def _partner() -> AnonSystemPartner:
    # Injected diagnostics/state keep the test hermetic (no DB, no /tmp state).
    return AnonSystemPartner(
        diagnostic_engine=_PassingDiagnostics(),
        dead_man_switch=TrustEngineDeadManSwitch(),
    )


def _failing_report() -> SystemHealthReport:
    return SystemHealthReport(
        overall_status=CheckStatus.CRITICAL_FAILURE, checks_passed=2, checks_remediated=0,
        checks_warned=0, checks_failed=1,
        results=[DiagnosticCheckResult(
            check_name="DB Isolation", category="database", status=CheckStatus.CRITICAL_FAILURE,
            latency_ms=1.0, message="isolation level wrong",
        )],
    )


def test_routine_check():
    assert "smooth as butter" in _partner().run_routine_check()


def test_conversational_status_query():
    for q in ("How's the system looking?", "status?", "any health issues"):
        assert "smooth as butter" in _partner().respond_to_user(q), q


def test_lockdown_and_override():
    partner = _partner()
    for _ in range(3):
        out = partner.ingest_report(_failing_report())
    assert partner.dead_man_switch.current_state == SwitchState.LOCKED_DOWN
    assert "DB Isolation" in out
    assert "DB Isolation" in partner.run_routine_check()
    assert "trustee" in partner.respond_to_user("How do we reset this lockdown?")


def test_override_when_armed():
    assert "already open" in _partner().respond_to_user("override please")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
