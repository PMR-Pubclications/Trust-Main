CREATE TABLE legacy_trust_admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'ADMIN',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agency_rfid_badges (
    badge_id INT PRIMARY KEY AUTO_INCREMENT,
    card_uid VARCHAR(128) UNIQUE NOT NULL,
    admin_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES legacy_trust_admins(admin_id) ON DELETE CASCADE
);


-- Example Admin User (Password should be pre-hashed, e.g., via BCrypt)
-- INSERT INTO legacy_trust_admins (username, password_hash, role) 
-- VALUES ('admin_trust', '$2a$10$YourHashedPasswordHere...', 'SUPER_ADMIN');



CREATE TABLE IF NOT EXISTS legacy_trust_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    sha256_hash VARCHAR(64) UNIQUE NOT NULL,
    submitter_role VARCHAR(100) NOT NULL,
    intake_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
