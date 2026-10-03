import csv
import hashlib
import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct

from postgres_ledger_adapter import LiveTrialBalance, AccountBalance
from trust_rule_enforcer import EnforcerResult, TierLevel


# ==========================================
# 1. Audit Trail Models & Artifacts
# ==========================================
class AuditTrailPayload(BaseModel):
    audit_id: str
    trust_id: str
    disbursement_id: str
    tier: TierLevel
    amount: Decimal
    destination_account: str
    executed_at: datetime
    trial_balance: LiveTrialBalance
    verified_trustees: List[str]
    payment_reference: Optional[str] = None
    rail_used: Optional[str] = None

    def to_canonical_bytes(self) -> bytes:
        """Generates a deterministic UTF-8 byte stream of the audit payload for signing."""
        canonical_dict = {
            "audit_id": self.audit_id,
            "trust_id": self.trust_id,
            "disbursement_id": self.disbursement_id,
            "tier": self.tier.value,
            "amount": f"{self.amount:.2f}",
            "destination_account": self.destination_account,
            "executed_at": self.executed_at.isoformat(),
            "trial_balance": {
                "is_balanced": self.trial_balance.is_balanced,
                "total_debits": f"{self.trial_balance.total_debits:.2f}",
                "total_credits": f"{self.trial_balance.total_credits:.2f}",
                "imbalance_delta": f"{self.trial_balance.imbalance_delta:.2f}",
                "accounts": [
                    {
                        "account_id": acc.account_id,
                        "account_number": acc.account_number,
                        "account_name": acc.account_name,
                        "account_type": acc.account_type.value,
                        "net_balance": f"{acc.net_balance:.2f}"
                    }
                    for acc in self.trial_balance.accounts
                ]
            },
            "verified_trustees": sorted(self.verified_trustees),
            "payment_reference": self.payment_reference or "",
            "rail_used": self.rail_used or ""
        }
        return json.dumps(canonical_dict, sort_keys=True, separators=(',', ':')).encode('utf-8')


class SignedAuditReport(BaseModel):
    audit_id: str
    payload: AuditTrailPayload
    digest_sha256: str
    signing_authority_address: str
    signature_hex: str
    signed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# 2. Audit Trail Reporter Utility
# ==========================================
class AuditTrailReporter:
    """
    Generates, signs, and exports immutable audit trails for Tier 3/4 capital releases.
    """

    def __init__(self, signing_private_key_hex: Optional[str] = None):
        """
        :param signing_private_key_hex: ECDSA private key for the auditor/compliance engine.
                                       If omitted, an ephemeral key is generated.
        """
        if signing_private_key_hex:
            self.account = EthAccount.from_key(signing_private_key_hex)
        else:
            self.account = EthAccount.create()

    @property
    def auditor_address(self) -> str:
        return self.account.address

    def generate_signed_audit_trail(
        self,
        trust_id: str,
        destination_account: str,
        amount: Decimal,
        enforcer_result: EnforcerResult,
        trial_balance_snapshot: LiveTrialBalance
    ) -> SignedAuditReport:
        """
        Creates an audit payload combining transaction execution details, trustee proofs,
        and PostgreSQL trial balance state, then cryptographically signs it.
        """
        now = datetime.now(timezone.utc)
        audit_id = f"aud_{enforcer_result.disbursement_id}_{int(now.timestamp())}"

        # Extract payment rail details if available
        payment_ref = None
        rail_used = None
        if enforcer_result.execution_receipt:
            payment_ref = enforcer_result.execution_receipt.transaction_reference
            rail_used = enforcer_result.execution_receipt.rail.value

        # Extract trustee verification list
        verified_trustees = []
        if enforcer_result.signature_report:
            verified_trustees = enforcer_result.signature_report.get("verified_trustees", [])

        # Construct Payload
        payload = AuditTrailPayload(
            audit_id=audit_id,
            trust_id=trust_id,
            disbursement_id=enforcer_result.disbursement_id,
            tier=enforcer_result.tier,
            amount=amount,
            destination_account=destination_account,
            executed_at=now,
            trial_balance=trial_balance_snapshot,
            verified_trustees=verified_trustees,
            payment_reference=payment_ref,
            rail_used=rail_used
        )

        # Compute SHA-256 Digest & Sign EIP-191 Message
        raw_bytes = payload.to_canonical_bytes()
        digest_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        
        signable_msg = encode_defunct(primitive=raw_bytes)
        signature = self.account.sign_message(signable_msg).signature.hex()

        return SignedAuditReport(
            audit_id=audit_id,
            payload=payload,
            digest_sha256=digest_sha256,
            signing_authority_address=self.account.address,
            signature_hex=signature,
            signed_at=now
        )

    def verify_audit_report_integrity(self, report: SignedAuditReport) -> bool:
        """Cryptographically verifies report signature and data integrity."""
        raw_bytes = report.payload.to_canonical_bytes()
        expected_digest = hashlib.sha256(raw_bytes).hexdigest()

        if expected_digest != report.digest_sha256:
            return False

        try:
            signable_msg = encode_defunct(primitive=raw_bytes)
            recovered = EthAccount.recover_message(signable_msg, signature=report.signature_hex)
            return recovered.lower() == report.signing_authority_address.lower()
        except Exception:
            return False

    def export_to_json(self, report: SignedAuditReport, file_path: str) -> None:
        """Exports the signed audit report artifact to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

    def export_to_csv(self, report: SignedAuditReport, file_path: str) -> None:
        """
        Exports a flat CSV audit breakdown containing execution headers
        and individual PostgreSQL trial balance line items.
        """
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Metadata Header Rows
            writer.writerow(["=== AUDIT TRAIL CERTIFICATE ==="])
            writer.writerow(["Audit ID", report.audit_id])
            writer.writerow(["Trust ID", report.payload.trust_id])
            writer.writerow(["Disbursement ID", report.payload.disbursement_id])
            writer.writerow(["Tier", report.payload.tier.value])
            writer.writerow(["Amount Released", f"${report.payload.amount:,.2f}"])
            writer.writerow(["Destination Account", report.payload.destination_account])
            writer.writerow(["Payment Rail", report.payload.rail_used or "N/A"])
            writer.writerow(["Payment Reference", report.payload.payment_reference or "N/A"])
            writer.writerow(["Verified Trustees", " | ".join(report.payload.verified_trustees)])
            writer.writerow(["Executed At", report.payload.executed_at.isoformat()])
            writer.writerow(["SHA-256 Digest", report.digest_sha256])
            writer.writerow(["Auditor Address", report.signing_authority_address])
            writer.writerow(["Signature Hex", report.signature_hex])
            writer.writerow([])

            # Trial Balance Header Rows
            writer.writerow(["=== POSTGRESQL TRIAL BALANCE SNAPSHOT AT RELEASE ==="])
            writer.writerow(["Trial Balance Balanced?", report.payload.trial_balance.is_balanced])
            writer.writerow(["Total Debits", f"${report.payload.trial_balance.total_debits:,.2f}"])
            writer.writerow(["Total Credits", f"${report.payload.trial_balance.total_credits:,.2f}"])
            writer.writerow([])

            # Table Header
            writer.writerow([
                "Account Number",
                "Account ID",
                "Account Name",
                "Account Type",
                "Total Debits",
                "Total Credits",
                "Net Balance"
            ])

            # Table Rows
            for acc in report.payload.trial_balance.accounts:
                writer.writerow([
                    acc.account_number,
                    acc.account_id,
                    acc.account_name,
                    acc.account_type.value,
                    f"{acc.total_debits:.2f}",
                    f"{acc.total_credits:.2f}",
                    f"{acc.net_balance:.2f}"
                ])
