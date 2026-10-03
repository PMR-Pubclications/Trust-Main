-- Chart of Accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(32) NOT NULL, -- Asset, Liability, Equity, Revenue, Expense
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Immutable Journal Store
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT NOT NULL,
    reference_id VARCHAR(128), -- Invoice ID, Trade ID, Transaction Hash
    status VARCHAR(32) NOT NULL CHECK (status IN ('POSTED', 'REVERSED')),
    posted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Atomic Postings (Atomic invariant: SUM(amount) WHERE entry_id = X must be 0)
CREATE TABLE postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID REFERENCES journal_entries(id),
    account_id UUID REFERENCES accounts(id),
    amount NUMERIC(18, 4) NOT NULL, -- Positive for Debit, Negative for Credit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Materialized View for Quick Balance Checks
CREATE MATERIALIZED VIEW account_balances AS
SELECT 
    account_id,
    SUM(amount) AS ledger_balance
FROM postings
GROUP BY account_id;
