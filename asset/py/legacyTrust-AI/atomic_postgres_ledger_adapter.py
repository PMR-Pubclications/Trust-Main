import os
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import psycopg
from psycopg import IsolationLevel
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, model_validator

# Reuse AccountType and LiveTrialBalance models
from postgres_ledger_adapter import AccountType, AccountBalance, LiveTrialBalance


class DisbursementPostingRequest(BaseModel):
    trust_id: str
    disbursement_id: str
    debit_account_id: str   # e.g., Expense / Distribution account
    credit_account_id: str  # e.g., Cash / Liquid Asset account
    amount: Decimal
    description: str = Field(default="Tier 3/4 Multi-Sig Approved Disbursement")

    @field_validator("amount")
    def validate_positive_amount(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0.00"):
            raise ValueError("Disbursement amount must be strictly greater than zero.")
        return v


class AtomicPostingReceipt(BaseModel):
    entry_id: str
    disbursement_id: str
    posted_at: datetime
    debit_account_id: str
    credit_account_id: str
    amount: Decimal
    isolation_level: str = "SERIALIZABLE"


class AtomicPostgresLedgerAdapter:
    """
    Thread-safe, high-concurrency database adapter that locks target account rows
    using SELECT FOR UPDATE under SERIALIZABLE isolation during disbursement execution.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "POSTGRES_LEDGER_URL",
            "postgresql://ledger_user:ledger_pass@localhost:5432/trust_ledger"
        )

    def execute_locked_disbursement(
        self,
        posting_request: DisbursementPostingRequest
    ) -> AtomicPostingReceipt:
        """
        Executes an atomic double-entry posting:
        1. Begins a transaction with SERIALIZABLE isolation level.
        2. Locks target accounts using 'SELECT ... FOR UPDATE' sorted by account_id to prevent deadlocks.
        3. Verifies credit account balance under lock.
        4. Inserts posted journal entry and double-entry lines into PostgreSQL.
        5. Commits atomically or rolls back entirely on failure.
        """
        now = datetime.now(timezone.utc)
        entry_id = f"je_{posting_request.disbursement_id}_{int(now.timestamp())}"

        # Order account IDs deterministically to prevent database deadlocks across concurrent requests
        locked_account_ids = sorted([posting_request.debit_account_id, posting_request.credit_account_id])

        with psycopg.connect(self.connection_string, row_factory=dict_row) as conn:
            # Set transaction to highest isolation level
            conn.isolation_level = IsolationLevel.SERIALIZABLE

            with conn.transaction():
                with conn.cursor() as cur:
                    # 1. Acquire Row-Level Locks (SELECT FOR UPDATE) on involved accounts
                    lock_query = """
                        SELECT 
                            a.account_id,
                            a.account_name,
                            a.account_type,
                            COALESCE(SUM(CASE WHEN jl.entry_type = 'DEBIT' THEN jl.amount ELSE 0 END), 0.0) AS total_debits,
                            COALESCE(SUM(CASE WHEN jl.entry_type = 'CREDIT' THEN jl.amount ELSE 0 END), 0.0) AS total_credits
                        FROM accounts a
                        LEFT JOIN journal_lines jl ON a.account_id = jl.account_id
                        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.status = 'POSTED'
                        WHERE a.trust_id = %(trust_id)s
                          AND a.account_id = ANY(%(account_ids)s)
                        GROUP BY a.account_id, a.account_name, a.account_type
                        ORDER BY a.account_id ASC
                        FOR UPDATE OF a;
                    """
                    
                    cur.execute(lock_query, {
                        "trust_id": posting_request.trust_id,
                        "account_ids": locked_account_ids
                    })
                    locked_rows = {row["account_id"]: row for row in cur.fetchall()}

                    # Verify both accounts exist in the ledger
                    if len(locked_rows) < 2:
                        missing = set(locked_account_ids) - set(locked_rows.keys())
                        raise ValueError(f"ATOMIC_LOCK_FAILED: Target account(s) {missing} not found.")

                    # 2. Check Credit Account Solvency Under Lock
                    credit_account = locked_rows[posting_request.credit_account_id]
                    credit_debits = Decimal(str(credit_account["total_debits"]))
                    credit_credits = Decimal(str(credit_account["total_credits"]))
                    
                    # Calculate net liquid balance (Assets are Debits - Credits)
                    if credit_account["account_type"] == "ASSET":
                        current_liquid_balance = credit_debits - credit_credits
                    else:
                        current_liquid_balance = credit_credits - credit_debits

                    if current_liquid_balance < posting_request.amount:
                        raise ValueError(
                            f"INSUFFICIENT_FUNDS_UNDER_LOCK: Account '{credit_account['account_name']}' "
                            f"has balance ${current_liquid_balance:,.2f}, but disbursement requires ${posting_request.amount:,.2f}."
                        )

                    # 3. Insert Journal Entry Header
                    cur.execute(
                        """
                        INSERT INTO journal_entries (entry_id, trust_id, posted_at, status)
                        VALUES (%(entry_id)s, %(trust_id)s, %(posted_at)s, 'POSTED');
                        """,
                        {
                            "entry_id": entry_id,
                            "trust_id": posting_request.trust_id,
                            "posted_at": now
                        }
                    )

                    # 4. Insert Double-Entry Journal Lines (Debit Expense/Distribution, Credit Asset)
                    lines = [
                        (f"line_{entry_id}_1", entry_id, posting_request.debit_account_id, "DEBIT", posting_request.amount),
                        (f"line_{entry_id}_2", entry_id, posting_request.credit_account_id, "CREDIT", posting_request.amount)
                    ]

                    cur.executemany(
                        """
                        INSERT INTO journal_lines (line_id, entry_id, account_id, entry_type, amount)
                        VALUES (%s, %s, %s, %s, %s);
                        """,
                        lines
                    )

        # Transaction automatically committed if block completes without exception
        return AtomicPostingReceipt(
            entry_id=entry_id,
            disbursement_id=posting_request.disbursement_id,
            posted_at=now,
            debit_account_id=posting_request.debit_account_id,
            credit_account_id=posting_request.credit_account_id,
            amount=posting_request.amount,
            isolation_level="SERIALIZABLE"
        )
