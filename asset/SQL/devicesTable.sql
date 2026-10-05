-- Trust-Main Central Device Registry
CREATE TABLE registered_devices (
    hardware_uuid VARCHAR(64) PRIMARY KEY, -- Hardware Serial / Android ID / Secure Element Hash
    agency_id VARCHAR(32) NOT NULL,        -- e.g., 'POLICE', 'FIRE', 'EMS'
    provisioned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    initial_ip VARCHAR(45) NOT NULL,
    last_known_ip VARCHAR(45) NOT NULL,
    status VARCHAR(16) DEFAULT 'LOCKED_ACTIVE',
    
    -- Ensure agency_id can never be set back to NULL or updated once assigned
    CONSTRAINT chk_agency_not_empty CHECK (length(agency_id) > 0)
);

-- Audit log for network identity tracking across re-installs
CREATE TABLE device_network_audit (
    audit_id SERIAL PRIMARY KEY,
    hardware_uuid VARCHAR(64) REFERENCES registered_devices(hardware_uuid),
    ip_address VARCHAR(45) NOT NULL,
    event_type VARCHAR(32) NOT NULL, -- 'HANDSHAKE', 'REINSTALL_CHECK', 'SYNC'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
