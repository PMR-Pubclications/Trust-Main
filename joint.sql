-- =========================================================================
-- 1. OPERATIONAL & TRUST RECORDS (Unified Partition Storage)
-- =========================================================================
CREATE TABLE operational_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    payload BYTEA NOT NULL,
    security_tag VARCHAR(32) NOT NULL DEFAULT 'TRUST_EXCLUSIVE' 
        CHECK (security_tag IN ('PUBLIC', 'FIRST_RESPONDER', 'TRUST_EXCLUSIVE')),
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for rapid filtering by security partition
CREATE INDEX idx_operational_records_security_tag ON operational_records(security_tag);


-- =========================================================================
-- 2. TRUST & AGENCY ADMINISTRATORS
-- =========================================================================
CREATE TABLE legacy_trust_admins (
    admin_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'ADMIN',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================================
-- 3. PHYSICAL HARDWARE / RFID BADGE ACCESS
-- =========================================================================
CREATE TABLE agency_rfid_badges (
    badge_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    card_uid VARCHAR(128) UNIQUE NOT NULL,
    admin_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admin_badge FOREIGN KEY (admin_id) 
        REFERENCES legacy_trust_admins(admin_id) ON DELETE CASCADE
);

CREATE INDEX idx_agency_rfid_card_uid ON agency_rfid_badges(card_uid);


-- =========================================================================
-- 4. IMMUTABLE CRYPTOGRAPHIC REPORT LOGS
-- =========================================================================
CREATE TABLE IF NOT EXISTS legacy_trust_reports (
    report_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    sha256_hash VARCHAR(64) UNIQUE NOT NULL,
    submitter_role VARCHAR(100) NOT NULL,
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_legacy_trust_reports_hash ON legacy_trust_reports(sha256_hash);
