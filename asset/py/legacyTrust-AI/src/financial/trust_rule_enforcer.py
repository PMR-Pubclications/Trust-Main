import json
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

# Imports from previous cryptographic & database modules
from trust_signature_verifier import (
    TrustSignatureVerifier,
    TrusteeSignature,
    CanonicalTransactionPayload,
    VerificationStatus
)
from postgres_ledger_adapter import (
    PostgresLedgerAdapter,
    AccountType,
    LiveTrialBalance
)


# ==========================================
# 1. Payment Rail Interfaces (Plaid & Alpaca)
# ==========================================
class PaymentRail(str, Enum):
    PLAID_ACH = "PLAID_ACH"
    ALPACA_WIRE = "ALPACA_WIRE"


class ExecutionReceipt(BaseModel):
    disbursement_id: str
    status: str
    rail: PaymentRail
    transaction_reference: str
    amount: Decimal
    destination_account: str
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlaidDisbursementClient:
    """Mock/Wrapper interface for Plaid Transfer API (ACH disbursements)."""
    def execute_ach_transfer(self, disbursement_id: str, amount: Decimal, destination_account_id: str) -> str:
        # In production: call plaid_client.transfer_authorization_create() & transfer_create()
        ref = f"plaid_ach_tx_{disbursement_id[:8]}_{int(datetime.now().timestamp())}"
        return ref


class AlpacaDisbursementClient:
    """Mock/Wrapper interface for Alpaca Brokerage Wire / Cash Transfer API."""
    def execute_wire_transfer(self, disbursement_id: str, amount: Decimal, destination_account_id: str) -> str:
        # In production: call alpaca_client.create_payout_wire()
        ref = f"alpaca_wire_tx_{disbursement_id[:8]}_{int(datetime.now().timestamp())}"
        return ref


# ==========================================
# 2. Tier Policy Configuration Models
# ==========================================
class TierLevel(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
    TIER_4 = "TIER_4"


class TierPolicy(BaseModel):
    tier: TierLevel
    max_amount: Decimal
    required_quorum: int
    allowed_roles: List[str]
    default_rail: PaymentRail


# Default Governance Policy Rules for Disbursement Tiers
DEFAULT_TIER_POLICIES: Dict[TierLevel, TierPolicy] = {
    TierLevel.TIER_1: TierPolicy(
        tier=TierLevel.TIER_1,
        max_amount=Decimal("5000.00"),
        required_quorum=1,
        allowed_roles=["MANAGING_TRUSTEE", "DELEGATED_OFFICER"],
        default_rail=PaymentRail.PLAID_ACH
    ),
    TierLevel.TIER_2: TierPolicy(
        tier=TierLevel.TIER_2,
        max_amount=Decimal("25000.00"),
        required_quorum=1,
        allowed_roles=["MANAGING_TRUSTEE"],
        default_rail=PaymentRail.PLAID_ACH
    ),
    TierLevel.TIER_3: TierPolicy(
        tier=TierLevel.TIER_3,
        max_amount=Decimal("100000.00"),
        required_quorum=2,
        allowed_roles=["MANAGING_TRUSTEE", "INDEPENDENT_TRUSTEE"],
        default_rail=PaymentRail.PLAID_ACH
    ),
    TierLevel.TIER_4: TierPolicy(
        tier=TierLevel.TIER_4,
        max_amount=Decimal("100000000.00"),  # High capital cap
        required_quorum=3,
        allowed_roles=["MANAGING_TRUSTEE", "INDEPENDENT_TRUSTEE", "PROTECTOR"],
        default_rail=PaymentRail.ALPACA_WIRE
    ),
}


# ==========================================
# 3. Unified Trust Rule Enforcer Engine
# ==========================================
class EnforcerResult(BaseModel):
    disbursement_id: str
    approved: bool
    tier: TierLevel
    reason: str
    trial_balance_verified: bool
    signature_report: Optional[Dict] = None
    execution_receipt: Optional[ExecutionReceipt] = None


class TrustRuleEnforcer:
    """
    End-to-end governance gateway:
    1. Validates PostgreSQL trial balance double-entry integrity & liquid solvency.
    2. Validates cryptographic trustee signatures against tier multi-sig requirements.
    3. Dispatches disbursements through Plaid or Alpaca upon full clearance.
    """

    def __init__(
        self,
        policy_governance: Dict,
        ledger_adapter: PostgresLedgerAdapter,
        plaid_client: Optional[PlaidDisbursementClient] = None,
        alpaca_client: Optional[AlpacaDisbursementClient] = None,
        tier_policies: Optional[Dict[TierLevel, TierPolicy]] = None
    ):
        self.policy_governance = policy_governance
        self.ledger_adapter = ledger_adapter
        self.signature_verifier = TrustSignatureVerifier(policy_governance)
        self.plaid_client = plaid_client or PlaidDisbursementClient()
        self.alpaca_client = alpaca_client or AlpacaDisbursementClient()
        self.tier_policies = tier_policies or DEFAULT_TIER_POLICIES

    def evaluate_and_execute_disbursement(
        self,
        payload: CanonicalTransactionPayload,
        tier: TierLevel,
        signatures: List[TrusteeSignature],
        override_rail: Optional[PaymentRail] = None
    ) -> EnforcerResult:
        """
        Processes a Tier 3/4 disbursement request through solvency checks, 
        cryptographic quorum verification, and payment rail dispatch.
        """
        tier_policy = self.tier_policies.get(tier)
        if not tier_policy:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"INVALID_TIER: Config for '{tier}' not defined in governance policy.",
                trial_balance_verified=False
            )

        # ---------------------------------------------------------
        # STEP 1: Verify Amount Cap for Target Tier
        # ---------------------------------------------------------
        if payload.amount > tier_policy.max_amount:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"AMOUNT_EXCEEDS_TIER_CAP: Requested ${payload.amount:,.2f} exceeds max ${tier_policy.max_amount:,.2f} for {tier.value}.",
                trial_balance_verified=False
            )

        # ---------------------------------------------------------
        # STEP 2: PostgreSQL Double-Entry Solvency Verification
        # ---------------------------------------------------------
        try:
            trial_balance = self.ledger_adapter.fetch_live_trial_balance(payload.trust_id)
        except Exception as e:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"DATABASE_ERROR: Failed to pull live trial balance: {str(e)}",
                trial_balance_verified=False
            )

        # Enforce fundamental trial balance identity (Sum Debits == Sum Credits)
        if not trial_balance.is_balanced:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"LEDGER_DRIFT_ERROR: Live PostgreSQL trial balance is unbalanced by ${trial_balance.imbalance_delta:.2f}. Execution halted.",
                trial_balance_verified=False
            )

        # Check total liquid asset balance
        total_liquid_assets = sum(
            acc.net_balance 
            for acc in trial_balance.accounts 
            if acc.account_type == AccountType.ASSET
        )

        if total_liquid_assets < payload.amount:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"INSUFFICIENT_LIQUIDITY: Available asset funds (${total_liquid_assets:,.2f}) are less than requested (${payload.amount:,.2f}).",
                trial_balance_verified=True
            )

        # ---------------------------------------------------------
        # STEP 3: Cryptographic Signature Verification
        # ---------------------------------------------------------
        sig_report = self.signature_verifier.verify_transaction_release(
            payload=payload,
            signatures=signatures,
            required_signatures=tier_policy.required_quorum,
            allowed_roles=tier_policy.allowed_roles
        )

        if sig_report.status != VerificationStatus.RELEASE_APPROVED:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"SIGNATURE_VERIFICATION_FAILED: {'; '.join(sig_report.errors)}",
                trial_balance_verified=True,
                signature_report=sig_report.model_dump()
            )

        # ---------------------------------------------------------
        # STEP 4: Payment Rail Dispatch (Plaid vs Alpaca)
        # ---------------------------------------------------------
        selected_rail = override_rail or tier_policy.default_rail

        if selected_rail == PaymentRail.PLAID_ACH:
            tx_ref = self.plaid_client.execute_ach_transfer(
                disbursement_id=payload.disbursement_id,
                amount=payload.amount,
                destination_account_id=payload.destination_account_id
            )
        elif selected_rail == PaymentRail.ALPACA_WIRE:
            tx_ref = self.alpaca_client.execute_wire_transfer(
                disbursement_id=payload.disbursement_id,
                amount=payload.amount,
                destination_account_id=payload.destination_account_id
            )
        else:
            return EnforcerResult(
                disbursement_id=payload.disbursement_id,
                approved=False,
                tier=tier,
                reason=f"UNSUPPORTED_RAIL: Payment rail '{selected_rail}' is not implemented.",
                trial_balance_verified=True,
                signature_report=sig_report.model_dump()
            )

        execution_receipt = ExecutionReceipt(
            disbursement_id=payload.disbursement_id,
            status="EXECUTED",
            rail=selected_rail,
            transaction_reference=tx_ref,
            amount=payload.amount,
            destination_account=payload.destination_account_id
        )

        return EnforcerResult(
            disbursement_id=payload.disbursement_id,
            approved=True,
            tier=tier,
            reason=f"SUCCESS: Tier {tier.value} transaction verified and dispatched via {selected_rail.value}.",
            trial_balance_verified=True,
            signature_report=sig_report.model_dump(),
            execution_receipt=execution_receipt
        )
