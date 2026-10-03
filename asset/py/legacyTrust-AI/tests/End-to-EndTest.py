from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct
from postgres_ledger_adapter import AccountBalance

if __name__ == "__main__":
    print("=== TESTING UNIFIED TRUST RULE ENFORCER ===")

    # 1. Generate Trustee Keys
    trustee1_acc = EthAccount.create()
    trustee2_acc = EthAccount.create()

    # 2. Define Governance Policy Setup
    governance_policy = {
        "trustees": [
            {
                "id": "tru_01",
                "name": "Managing Trustee",
                "role": "MANAGING_TRUSTEE",
                "pubkey_or_address": trustee1_acc.address
            },
            {
                "id": "tru_02",
                "name": "Independent Trustee",
                "role": "INDEPENDENT_TRUSTEE",
                "pubkey_or_address": trustee2_acc.address
            }
        ]
    }

    # 3. Create Mock Ledger Adapter with Valid Double-Entry Balances ($250k Cash vs Equity)
    class MockPostgresLedgerAdapter(PostgresLedgerAdapter):
        def fetch_live_trial_balance(self, trust_id: str, as_of=None) -> LiveTrialBalance:
            accounts = [
                AccountBalance(
                    account_id="acc_1010",
                    account_number="1010",
                    account_name="Operating Cash Reserve",
                    account_type=AccountType.ASSET,
                    total_debits=Decimal("250000.00"),
                    total_credits=Decimal("0.00")
                ),
                AccountBalance(
                    account_id="acc_3010",
                    account_number="3010",
                    account_name="Trust Corpus Equity",
                    account_type=AccountType.EQUITY,
                    total_debits=Decimal("0.00"),
                    total_credits=Decimal("250000.00")
                )
            ]
            return LiveTrialBalance(trust_id=trust_id, accounts=accounts)

    mock_adapter = MockPostgresLedgerAdapter()
    enforcer = TrustRuleEnforcer(
        policy_governance=governance_policy,
        ledger_adapter=mock_adapter
    )

    # 4. Construct Tier 3 Transaction Payload ($75,000 Disbursement)
    payload = CanonicalTransactionPayload(
        trust_id="trst_legacy_alpha_01",
        disbursement_id="tx_tier3_capital_75k",
        amount=Decimal("75000.00"),
        destination_account_id="acc_vendor_payout_884",
        nonce="nonce_20261003_002"
    )

    # 5. Sign Payload with Both Required Trustees
    signable_msg = encode_defunct(primitive=payload.to_canonical_bytes())
    sig1_hex = trustee1_acc.sign_message(signable_msg).signature.hex()
    sig2_hex = trustee2_acc.sign_message(signable_msg).signature.hex()

    signatures = [
        TrusteeSignature(
            trustee_id="tru_01",
            pubkey_or_address=trustee1_acc.address,
            scheme="EVM_ECDSA",
            signature_hex=sig1_hex
        ),
        TrusteeSignature(
            trustee_id="tru_02",
            pubkey_or_address=trustee2_acc.address,
            scheme="EVM_ECDSA",
            signature_hex=sig2_hex
        )
    ]

    # 6. Evaluate and Execute Tier 3 Request
    result = enforcer.evaluate_and_execute_disbursement(
        payload=payload,
        tier=TierLevel.TIER_3,
        signatures=signatures
    )

    print("\n--- ENFORCEMENT & EXECUTION RESULT ---")
    print(f"Approved:               {result.approved}")
    print(f"Tier Level:             {result.tier.value}")
    print(f"Trial Balance Status:   {'PASSED' if result.trial_balance_verified else 'FAILED'}")
    print(f"Enforcement Summary:    {result.reason}")
    if result.execution_receipt:
        print(f"Execution Rail:         {result.execution_receipt.rail.value}")
        print(f"Payment Reference:      {result.execution_receipt.transaction_reference}")
