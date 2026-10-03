if __name__ == "__main__":
    print("=== TESTING ANON SYSTEM PARTNER ===")
    
    # Initialize partner
    partner = AnonSystemPartner()

    print("\n[Scenario 1: Routine Health Check]")
    print(partner.run_routine_check())
    print("-" * 50)

    print("\n[Scenario 2: Conversational Status Query]")
    print(partner.respond_to_user("How's the system looking?"))
    print("-" * 50)

    print("\n[Scenario 3: Simulating Lockdown Event]")
    # Force 3 failures on the switch
    failing_report = SystemHealthReport(
        overall_status=CheckStatus.CRITICAL_FAILURE,
        checks_passed=2,
        checks_remediated=0,
        checks_warned=0,
        checks_failed=1,
        results=[]
    )
    partner.dead_man_switch.process_health_report(failing_report)
    partner.dead_man_switch.process_health_report(failing_report)
    partner.dead_man_switch.process_health_report(failing_report)

    # Ask for status while locked down
    print(partner.run_routine_check())
    print("-" * 50)

    print("\n[Scenario 4: Asking About Override During Lockdown]")
    print(partner.respond_to_user("How do we reset this lockdown?"))
