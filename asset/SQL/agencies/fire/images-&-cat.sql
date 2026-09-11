-- =========================================================================
-- Agency Categories Schema
-- Save to: asset/SQL/agencies/categories/schema.sql
-- =========================================================================

CREATE TABLE IF NOT EXISTS agency_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    agency_domain VARCHAR(50) NOT NULL, -- LEGACY_TRUST, FIRE_AGENCY, POLICE_AGENCY
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial operational and trust categories
INSERT INTO agency_categories (agency_domain, category_name, description) VALUES
('LEGACY_TRUST', 'Financial Ledgers', 'Core financial records and trust asset allocations'),
('LEGACY_TRUST', 'Foster Campus Development', '20-acre Ridgefield trade school campus architectural and legal documents'),
('FIRE_AGENCY', 'Hazmat Incident Reports', 'Hazardous material responses, investigations, and safety logs'),
('FIRE_AGENCY', 'Fire Dispatch Logs', 'CAD logs and emergency response records'),
('POLICE_AGENCY', 'Digital Evidence Extractions', 'Forensic image dumps (.E01, .DD) and digital extractions'),
('POLICE_AGENCY', 'Crime Scene Media', 'Bodycam footage, CCTV captures, and photographic evidence');


-- =========================================================================
-- Binary Image & Blockchain Ledger Schema
-- Save to: asset/SQL/agencies/images/schema.sql
-- =========================================================================

CREATE TABLE IF NOT EXISTS agency_image_binaries (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL, -- e.g., image/png, image/jpeg
    image_binary LONGBLOB NOT NULL,   -- Raw binary payload for blockchain chunking / database storage
    sha256_hash VARCHAR(64) UNIQUE NOT NULL, -- Cryptographic anchor for on-chain verification
    blockchain_tx_id VARCHAR(255) DEFAULT NULL, -- Transaction hash once anchored to ledger
    uploaded_by VARCHAR(100) NOT NULL,
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES agency_categories(category_id)
);
