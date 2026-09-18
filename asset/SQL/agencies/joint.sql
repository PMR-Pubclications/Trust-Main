CREATE TABLE operational_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    payload BYTEA NOT NULL,
    security_tag VARCHAR(32) NOT NULL DEFAULT 'TRUST_EXCLUSIVE' 
        CHECK (security_tag IN ('PUBLIC', 'FIRST_RESPONDER', 'TRUST_EXCLUSIVE')),
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
