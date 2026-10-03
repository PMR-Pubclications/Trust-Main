-- General Ledger Schema Setup
CREATE TABLE accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    trust_id VARCHAR(64) NOT NULL,
    account_number VARCHAR(32) NOT NULL,
    account_name VARCHAR(128) NOT NULL,
    account_type VARCHAR(32) NOT NULL, -- ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    tier_restriction VARCHAR(16)        -- TIER_1, TIER_2, TIER_3, TIER_4
);

CREATE TABLE journal_entries (
    entry_id VARCHAR(64) PRIMARY KEY,
    trust_id VARCHAR(64) NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(32) NOT NULL DEFAULT 'POSTED' -- DRAFT, POSTED, REVERSED
);

CREATE TABLE journal_lines (
    line_id VARCHAR(64) PRIMARY KEY,
    entry_id VARCHAR(64) REFERENCES journal_entries(entry_id),
    account_id VARCHAR(64) REFERENCES accounts(account_id),
    entry_type VARCHAR(8) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    amount NUMERIC(18, 4) NOT NULL CHECK (amount > 0)
);
