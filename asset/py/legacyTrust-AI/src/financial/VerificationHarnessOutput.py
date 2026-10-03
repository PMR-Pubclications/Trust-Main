if __name__ == "__main__":
    print("=== RUNNING REMEDIATED DIAGNOSTIC SUITE ===")
    
    # Intentionally empty initial config to demonstrate auto-healing
    engine = TrustEngineSelfDiagnostic(policy_governance={"trustees": []})
    report = engine.run_full_diagnostic_suite()

    print(f"\nOverall Verdict: {report.overall_status.value}")
    print(f"Passed: {report.checks_passed} | Remediated: {report.checks_remediated} | Failures: {report.checks_failed}\n")

    for check in report.results:
        symbol = "✓" if check.status in (CheckStatus.PASSED, CheckStatus.REMEDIATED) else "✗"
        print(f"[{symbol}] {check.check_name:<40} -> {check.status.value}")
        print(f"    Message: {check.message}")
        if check.remediation_applied:
            print(f"    🔧 Auto-Remediation: {check.remediation_details}")
        print()
