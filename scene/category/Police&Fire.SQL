-- Create the main cases table to handle different investigation types
CREATE TABLE investigation_cases (
    case_id SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    investigation_type VARCHAR(30) CHECK (investigation_type IN ('Crime Scene', 'Arson Investigation')),
    investigator_lead VARCHAR(100) NOT NULL,
    date_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    case_status VARCHAR(30) DEFAULT 'Active'
);

-- Create a comprehensive evidence table capable of storing general, crime scene, and arson-specific data
CREATE TABLE scene_evidence (
    evidence_id SERIAL PRIMARY KEY,
    case_id INT REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    item_number VARCHAR(50) NOT NULL,
    general_category VARCHAR(50) NOT NULL, 
    -- General categories: Biological, Latent Print, Trace, Ballistics, Digital, Accelerant, Structural/Debris
    specific_category VARCHAR(50) NOT NULL,
    -- Specific categories: Blood, DNA Swab, Firearm, Liquid Accelerant, Charred Wood, Electrical Component
    description TEXT NOT NULL,
    collection_location VARCHAR(150) NOT NULL,
    collected_by VARCHAR(100) NOT NULL,
    date_collected TIMESTAMP NOT NULL,
    chain_of_custody_status VARCHAR(50) DEFAULT 'In Storage',
    
    -- Arson-specific attributes
    accelerant_detected BOOLEAN DEFAULT FALSE,
    accelerant_type VARCHAR(100), -- e.g., Gasoline, Diesel, Kerosene, Turpentine
    substrate_type VARCHAR(100), -- e.g., Wood flooring, Carpet, Drywall, Soil
    container_type VARCHAR(50), -- e.g., Paint can, Glass jar, Kapak bag
    lab_testing_required BOOLEAN DEFAULT TRUE,
    
    -- General Crime Scene attributes
    dna_profile_viable BOOLEAN,
    fingerprint_viable BOOLEAN,
    serial_number VARCHAR(100),
    storage_requirements VARCHAR(100) -- e.g., Frozen, Room Temp, Evidence Locker
);

-- Indexing for high-performance searching and filtering across investigations
CREATE INDEX idx_evidence_case ON scene_evidence(case_id);
CREATE INDEX idx_evidence_gen_cat ON scene_evidence(general_category);
CREATE INDEX idx_evidence_arson ON scene_evidence(accelerant_detected) WHERE accelerant_detected = TRUE;
