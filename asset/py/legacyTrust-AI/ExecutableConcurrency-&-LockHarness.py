if __name__ == "__main__":
    print("=== TESTING ATOMIC POSTGRES LEDGER POSTING WITH SELECT FOR UPDATE ===")

    # Request payload
    posting_req = DisbursementPostingRequest(
        trust_id="trst_legacy_alpha_01",
        disbursement_id="tx_tier3_capital_75k",
        debit_account_id="acc_5010_distributions",
        credit_account_id="acc_1010_operating_cash",
        amount=Decimal("75000.00"),
        description="Tier 3 Vendor Disbursement"
    )

    print(f"Disbursement ID:      {posting_req.disbursement_id}")
    print(f"Amount:               ${posting_req.amount:,.2f}")
    print(f"Target Accounts:      Debit [{posting_req.debit_account_id}] | Credit [{posting_req.credit_account_id}]")
    print(f"Lock Protocol:        SELECT FOR UPDATE (Sorted Account IDs)")
    print(f"Transaction Mode:     SERIALIZABLE")
