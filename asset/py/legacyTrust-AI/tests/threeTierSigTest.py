if __name__ == "__main__":
    print("=== GENERATING TRUSTEE TEST KEYS & SIGNATURES ===")
    
    # Generate 2 EVM Keys for Trustees
    acc1 = EthAccount.create()
    acc2 = EthAccount.create()

    # Governance policy setup with generated addresses
    governance_config = {
        "multisig_quorum": 2,
        "trustees": [
            {
                "id": "tru_01",
                "name": "Managing Trustee",
                "role": "MANAGING_TRUSTEE",
                "pubkey_or_address": acc1.address
            },
            {
                "id": "tru_02",
                "name": "Independent Trustee",
                "role": "INDEPENDENT_TRUSTEE",
                "pubkey_or_address": acc2.address
            }
        ]
    }

    # Initialize Verifier
    verifier = TrustSignatureVerifier(policy_governance=governance_config)

    # 1. Define Transaction Payload
    payload = CanonicalTransactionPayload(
        trust_id="trst_legacy_alpha_01",
        disbursement_id="tx_tier3_capital_50k",
        amount=Decimal("50000.00"),
        destination_account_id="acc_vendor_payout_90",
        nonce="nonce_20261003_001"
    )

    # 2. Sign Payload with Trustee Keys
    signable_msg = encode_defunct(primitive=payload.to_canonical_bytes())
    sig1_hex = acc1.sign_message(signable_msg).signature.hex()
    sig2_hex = acc2.sign_message(signable_msg).signature.hex()

    signatures = [
        TrusteeSignature(
            trustee_id="tru_01",
            pubkey_or_address=acc1.address,
            scheme=SignatureScheme.EVM_ECDSA,
            signature_hex=sig1_hex
        ),
        TrusteeSignature(
            trustee_id="tru_02",
            pubkey_or_address=acc2.address,
            scheme=SignatureScheme.EVM_ECDSA,
            signature_hex=sig2_hex
        )
    ]

    # 3. Verify Multi-Sig Release (Requires 2 signatures, roles: MANAGING_TRUSTEE / INDEPENDENT_TRUSTEE)
    report = verifier.verify_transaction_release(
        payload=payload,
        signatures=signatures,
        required_signatures=2,
        allowed_roles=["MANAGING_TRUSTEE", "INDEPENDENT_TRUSTEE"]
    )

    print("\n--- MULTI-SIG VERIFICATION REPORT ---")
    print(f"Status:             {report.status.value}")
    print(f"Valid Signatures:   {report.valid_signatures_count} / {report.required_signatures}")
    print(f"Verified Trustees:  {report.verified_trustees}")
    if report.errors:
        print(f"Errors/Warnings:    {report.errors}")
