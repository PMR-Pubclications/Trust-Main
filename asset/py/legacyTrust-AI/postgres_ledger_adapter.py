import os
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, List, Optional
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, model_validator


# ==========================================
# 1. Pydantic Models for Ledger & Trial Balance
# ==========================================
class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class AccountBalance(BaseModel):
    account_id: str
    account_number: str
    account_name: str
    account_type: AccountType
    tier_restriction: Optional[str] = None
    total_debits: Decimal = Field(default_factory=lambda: Decimal("0.00"))
    total_credits: Decimal = Field(default_factory=lambda: Decimal("0.00"))

    @property
    def net_balance(self) -> Decimal:
        """
        Calculates normal balance direction:
        - Assets / Expenses: Normal Debit (Debits - Credits)
        - Liabilities / Equity / Revenue: Normal Credit (Credits - Debits)
        """
        if self.account_type in (AccountType.ASSET, AccountType.EXPENSE):
            return self.total_debits - self.total_credits
        return self.total_credits - self.total_debits


class LiveTrialBalance(BaseModel):
    trust_id: str
    as_of_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accounts: List[AccountBalance]
    total_debits: Decimal = Field(default_factory=lambda: Decimal("0.00"))
    total_credits: Decimal = Field(default_factory=lambda: Decimal("0.00"))
    is_balanced: bool = False
    imbalance_delta: Decimal = Field(default_factory=lambda: Decimal("0.00"))

    @model_validator(mode="after")
    def validate_double_entry_equality(self) -> "LiveTrialBalance":
        """Enforces double-entry fundamental identity: Sum(Debits) == Sum(Credits)."""
        sum_debits = sum((acc.total_debits for acc in self.accounts), Decimal("0.00"))
        sum_credits = sum((acc.total_credits for acc in self.accounts), Decimal("0.00"))
        
        self.total_debits = sum_debits
        self.total_credits = sum_credits
        self.imbalance_delta = abs(sum_debits - sum_credits)
        
        # Micro-cent tolerance check
        self.is_balanced = self.imbalance_delta < Decimal("0.0001")
        return self


# ==========================================
# 2. Postgres Ledger Database Adapter
# ==========================================
class PostgresLedgerAdapter:
    """Extracts live trial balance data directly from PostgreSQL for rule enforcer feeds."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "POSTGRES_LEDGER_URL", 
            "postgresql://ledger_user:ledger_pass@localhost:5432/trust_ledger"
        )

    def fetch_live_trial_balance(
        self, 
        trust_id: str, 
        as_of: Optional[datetime] = None
    ) -> LiveTrialBalance:
        """
        Queries live ledger and aggregates total debits and credits per account up to `as_of`.
        """
        as_of_dt = as_of or datetime.now(timezone.utc)

        # SQL query calculating real-time sum of debits and credits per account
        query = """
            SELECT 
                a.account_id,
                a.account_number,
                a.account_name,
                a.account_type,
                a.tier_restriction,
                COALESCE(SUM(CASE WHEN jl.entry_type = 'DEBIT' THEN jl.amount ELSE 0 END), 0.0) AS total_debits,
                COALESCE(SUM(CASE WHEN jl.entry_type = 'CREDIT' THEN jl.amount ELSE 0 END), 0.0) AS total_credits
            FROM accounts a
            LEFT JOIN journal_lines jl ON a.account_id = jl.account_id
            LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id
            WHERE a.trust_id = %(trust_id)s
              AND (je.entry_id IS NULL OR (je.status = 'POSTED' AND je.posted_at <= %(as_of)s))
            GROUP BY a.account_id, a.account_number, a.account_name, a.account_type, a.tier_restriction
            ORDER BY a.account_number ASC;
        """

        account_balances: List[AccountBalance] = []

        with psycopg.connect(self.connection_string, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(query, {"trust_id": trust_id, "as_of": as_of_dt})
                rows = cur.fetchall()

                for row in rows:
                    account_balances.append(
                        AccountBalance(
                            account_id=row["account_id"],
                            account_number=row["account_number"],
                            account_name=row["account_name"],
                            account_type=AccountType(row["account_type"]),
                            tier_restriction=row["tier_restriction"],
                            total_debits=Decimal(str(row["total_debits"])),
                            total_credits=Decimal(str(row["total_credits"])),
                        )
                    )

        return LiveTrialBalance(
            trust_id=trust_id,
            as_of_timestamp=as_of_dt,
            accounts=account_balances
        )


# ==========================================
# 3. Rule Enforcer Feeding Engine
# ==========================================
class TrustLedgerRuleEnforcer:
    """Evaluates live accounting rules against the imported PostgreSQL trial balance."""

    def __init__(self, adapter: PostgresLedgerAdapter):
        self.adapter = adapter

    def verify_disbursement_feasibility(
        self, 
        trust_id: str, 
        requested_amount: Decimal, 
        tier_level: str
    ) -> Dict[str, any]:
        """
        Feeds live Postgres trial balance into governance checks:
        1. Double-Entry Invariant: Sum(Debits) == Sum(Credits)
        2. Solvency Check: Total Liquid Assets >= Requested Amount
        3. Tier Balance Rule: Ensures tier accounts hold sufficient backing.
        """
        trial_balance = self.adapter.fetch_live_trial_balance(trust_id)

        # 1. Fundamental Ledger Integrity Check
        if not trial_balance.is_balanced:
            return {
                "approved": False,
                "reason": f"CRITICAL: Ledger double-entry drift detected! Imbalance: ${trial_balance.imbalance_delta:.2f}",
                "trial_balance_status": "UNBALANCED"
            }

        # 2. Calculate Total Available Liquid Assets (Asset accounts marked for target tier or general)
        total_liquid_assets = sum(
            acc.net_balance 
            for acc in trial_balance.accounts 
            if acc.account_type == AccountType.ASSET 
            and (acc.tier_restriction is None or acc.tier_restriction == tier_level)
        )

        # 3. Solvency & Liquidity Evaluation
        if total_liquid_assets < requested_amount:
            return {
                "approved": False,
                "reason": f"INSUFFICIENT_FUNDS: Required ${requested_amount:.2f}, but Tier '{tier_level}' liquid pool holds${total_liquid_assets:.2f}",
                "liquid_balance": str(total_liquid_assets),
                "trial_balance_status": "BALANCED"
            }

        return {
            "approved": True,
            "reason": f"PASSED: Live PostgreSQL trial balance verified. Liquidity ${total_liquid_assets:.2f} covers${requested_amount:.2f}.",
            "liquid_balance": str(total_liquid_assets),
            "trial_balance_status": "BALANCED",
            "total_debits": str(trial_balance.total_debits),
            "total_credits": str(trial_balance.total_credits)
        }
