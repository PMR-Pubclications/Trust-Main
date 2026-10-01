SELECT * FROM operational_records;

SELECT record_id, title, intake_timestamp 
FROM operational_records 
WHERE security_tag = 'PUBLIC';

-- Registering a sensitive trust PDF record
INSERT INTO operational_records (title, payload, security_tag)
VALUES (
    'The Legacy Trust Declaration - Master Copy',
    E'\\x255044462d... [Binary data or file stream reference]',
    'TRUST_EXCLUSIVE'
);

-- Or logging the file path and cryptographic hash in your immutable reports table
INSERT INTO legacy_trust_reports (file_name, file_path, sha256_hash, submitter_role)
VALUES (
    'trust_declaration_2026.pdf',
    '/var/secure/trust_vault/trust_declaration_2026.pdf',
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'TRUST_ADMIN'
);



