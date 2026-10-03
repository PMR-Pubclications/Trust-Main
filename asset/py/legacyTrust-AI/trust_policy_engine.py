import yaml
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# ==========================================
# 1. Decision & Status Enums
# ==========================================
class EngineState(str, Enum):
    DORMANT_BYPASS = "DORMANT_BYPASS"  # Below NAV threshold; rules inactive
    ACTIVE_ENFORCEMENT = "ACTIVE_ENFORCEMENT"  # $5M+ NAV reached; strict governance active


class PolicyDecision(str, Enum):
    APPROVED_AUTO = "APPROVED_AUTO"
    REQUIRES_SINGLE_SIG = "REQUIRES_SINGLE_SIG"
    REQUIRES_MULTI_SIG = "REQUIRES_MULTI_SIG"
    REQUIRES_UNANIMOUS = "REQUIRES_UNANIMOUS"
    REJECTED_CONDITION_FAILED = "REJECTED_CONDITION_FAILED"
    REJECTED_EXCEEDS_CAPACITY = "REJECTED_EXCEEDS_CAPACITY"


# ==========================================
# 2. Input/Output Models
# ==========================================
class AccountBalance(BaseModel):
    account_id: str
    account_name: str
    balance: Decimal


class ProposedDisbursement(BaseModel):
    disbursement_id: str
    amount: Decimal
    description: str
    beneficiary_id: Optional[str] = None
    beneficiary_age: Optional[int] = None
    has_attached_proofs: bool = False
    gpa: Optional[float] = None


class EvaluationResult(BaseModel):
    disbursement_id: str
    engine_state: EngineState
    total_trust_nav: Decimal
    activation_threshold: Decimal
    decision: PolicyDecision
    applied_tier: Optional[int] = None
    required_signatures: int = 0
    allowed_roles: List[str] = Field(default_factory=list)
    timelock_hours: int = 0
    reason: str


# ==========================================
# 3. Trust Rule Enforcement Engine
# ==========================================
class TrustRuleEnforcer:
    def __init__(
        self,
        policy_yaml_path: str,
        activation_threshold: Decimal = Decimal("5000000.00")
    ):
        self.activation_threshold = Decimal(str(activation_threshold))
        self.policy = self._load_policy(policy_yaml_path)

    def _load_policy(self, path: str) -> Dict:
        """Parses and loads the YAML trust policy document."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load policy YAML from '{path}': {str(e)}")

    def calculate_total_nav(self, balances: List[AccountBalance]) -> Decimal:
        """Aggregates balances across all connected bank, brokerage, and ledger accounts."""
        return sum((acc.balance for acc in balances), Decimal("0.00"))

    def evaluate_disbursement(
        self,
        transaction: ProposedDisbursement,
        account_balances: List[AccountBalance]
    ) -> EvaluationResult:
        """
        Main Engine Algorithm:
        1. Audits total liquid NAV across all accounts.
        2. Evaluates NAV against activation gate ($5,000,000 threshold).
        3. If < $5M: Runs in DORMANT_BYPASS mode.
        4. If >= $5M: Runs ACTIVE_ENFORCEMENT (Tier checks, Quorums, Beneficiary Conditions).
        """
        total_nav = self.calculate_total_nav(account_balances)

        # -------------------------------------------------------------
        # ALGORITHM GATE 1: Check $5M Activation Threshold
        # -------------------------------------------------------------
        if total_nav < self.activation_threshold:
            return EvaluationResult(
                disbursement_id=transaction.disbursement_id,
                engine_state=EngineState.DORMANT_BYPASS,
                total_trust_nav=total_nav,
                activation_threshold=self.activation_threshold,
                decision=PolicyDecision.APPROVED_AUTO,
                applied_tier=None,
                required_signatures=0,
                allowed_roles=[],
                timelock_hours=0,
                reason=f"Trust rules dormant. Current NAV (${total_nav:,.2f}) is below the ${self.activation_threshold:,.2f} enforcement threshold."
            )

        # -------------------------------------------------------------
        # ALGORITHM GATE 2: Active Trust Enforcement ($5M+ NAV)
        # -------------------------------------------------------------
        
        # Step A: Evaluate Beneficiary Schedule Conditions (if applicable)
        if transaction.beneficiary_id:
            condition_passed, failure_reason = self._validate_beneficiary_conditions(transaction, total_nav)
            if not condition_passed:
                return EvaluationResult(
                    disbursement_id=transaction.disbursement_id,
                    engine_state=EngineState.ACTIVE_ENFORCEMENT,
                    total_trust_nav=total_nav,
                    activation_threshold=self.activation_threshold,
                    decision=PolicyDecision.REJECTED_CONDITION_FAILED,
                    reason=f"Beneficiary policy check failed: {failure_reason}"
                )

        # Step B: Determine Spending Tier & Multi-Sig Requirements
        amount = transaction.amount
        spending_tiers = self.policy.get("spending_thresholds", [])

        for tier in sorted(spending_tiers, key=lambda x: x["tier"]):
            min_amt = Decimal(str(tier["min_amount"]))
            max_amt = Decimal(str(tier["max_amount"])) if tier["max_amount"] is not None else None

            # Check if amount falls in current tier bracket
            if amount >= min_amt and (max_amt is None or amount <= max_amt):
                approval_type = tier["approval_type"]
                
                decision_map = {
                    "AUTO_APPROVED": PolicyDecision.APPROVED_AUTO,
                    "SINGLE_SIGNATURE": PolicyDecision.REQUIRES_SINGLE_SIG,
                    "MULTI_SIG": PolicyDecision.REQUIRES_MULTI_SIG,
                    "UNANIMOUS": PolicyDecision.REQUIRES_UNANIMOUS
                }

                return EvaluationResult(
                    disbursement_id=transaction.disbursement_id,
                    engine_state=EngineState.ACTIVE_ENFORCEMENT,
                    total_trust_nav=total_nav,
                    activation_threshold=self.activation_threshold,
                    decision=decision_map.get(approval_type, PolicyDecision.REQUIRES_MULTI_SIG),
                    applied_tier=tier["tier"],
                    required_signatures=tier["required_signatures"],
                    allowed_roles=tier.get("allowed_roles", []),
                    timelock_hours=tier.get("timelock_hours", 0),
                    reason=f"Enforcement active. Transaction matched Tier {tier['tier']} ({tier['name']})."
                )

        return EvaluationResult(
            disbursement_id=transaction.disbursement_id,
            engine_state=EngineState.ACTIVE_ENFORCEMENT,
            total_trust_nav=total_nav,
            activation_threshold=self.activation_threshold,
            decision=PolicyDecision.REJECTED_EXCEEDS_CAPACITY,
            reason="Transaction amount could not be categorized into configured tier brackets."
        )

    def _validate_beneficiary_conditions(self, tx: ProposedDisbursement, total_nav: Decimal) -> Tuple[bool, str]:
        """Evaluates conditional rules for beneficiary payouts."""
        schedules = self.policy.get("beneficiary_payouts", [])
        
        # Find schedule for beneficiary
        matched_schedule = next((s for s in schedules if s.get("beneficiary_id") == tx.beneficiary_id), None)
        if not matched_schedule:
            return True, "No specific conditions configured for this beneficiary."

        for cond in matched_schedule.get("conditions", []):
            cond_type = cond["type"]
            val = cond["value"]

            if cond_type == "AGE_GTE":
                if tx.beneficiary_age is None or tx.beneficiary_age < val:
                    return False, f"Beneficiary age ({tx.beneficiary_age}) is below minimum requirement of {val}."

            elif cond_type == "PORTFOLIO_NAV_GTE":
                if total_nav < Decimal(str(val)):
                    return False, f"Total NAV (${total_nav:,.2f}) is below schedule safety floor of ${Decimal(str(val)):,.2f}."

            elif cond_type == "MIN_GPA":
                if tx.gpa is None or tx.gpa < float(val):
                    return False, f"Beneficiary GPA ({tx.gpa}) does not meet academic requirement of {val}."

            elif cond_type == "PROOFS_ATTACHED":
                if val is True and not tx.has_attached_proofs:
                    return False, "Required invoice/transcript document proofs are missing."

        return True, "All beneficiary conditions satisfied."
