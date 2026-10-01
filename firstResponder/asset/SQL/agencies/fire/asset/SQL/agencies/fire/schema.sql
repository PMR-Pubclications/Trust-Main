CREATE TABLE IF NOT EXISTS fire_agency_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    sha256_hash VARCHAR(64) UNIQUE NOT NULL,
    submitter_role VARCHAR(100) NOT NULL,
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
