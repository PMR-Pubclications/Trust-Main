const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Initialize SQLite Database
const db = new sqlite3.Database('./governance.db', (err) => {
    if (err) console.error('Database connection error:', err.message);
    else console.log('Connected to the SQLite governance database.');
});

// Create Table
db.run(`CREATE TABLE IF NOT EXISTS onboarding_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_name TEXT NOT NULL,
    repo_name TEXT NOT NULL,
    organization TEXT,
    contact_email TEXT,
    github_private_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)`);

// Onboarding API Endpoint
app.post('/api/onboard', (req, res) => {
    const { owner_name, repo_name, organization, contact_email } = req.body;

    if (!owner_name || !repo_name) {
        return res.status(400).json({ error: 'Owner name and repository name are required.' });
    }

    try {
        // Generate a 2048-bit RSA Private Key for GitHub Integration
        const { privateKey } = crypto.generateKeyPairSync('rsa', {
            modulusLength: 2048,
            publicKeyEncoding: { type: 'spki', format: 'pem' },
            privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
        });

        // Insert into SQLite Database
        const query = `INSERT INTO onboarding_profiles (owner_name, repo_name, organization, contact_email, github_private_key) VALUES (?, ?, ?, ?, ?)`;
        
        db.run(query, [owner_name, repo_name, organization || 'PMR Publications', contact_email, privateKey], function(err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.json({
                success: true,
                message: 'Onboarding profile saved and private key generated successfully.',
                profile_id: this.lastID,
                generated_key_preview: privateKey.split('\n')[1] + '...' // Return preview snippet only for security
            });
        });

    } catch (err) {
        res.status(500).json({ error: 'Key generation failed: ' + err.message });
    }
});

app.listen(3000, () => {
    console.log('Governance onboarding server running on port 3000');
});
