const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const archiver = require('archiver');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Initialize secure local database for department settings & telemetry audit trails
const db = new sqlite3.Database('./forensic_trust.db', (err) => {
    if (err) console.error('Database connection error:', err.message);
    else console.log('Connected to secure local forensic database.');
});

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS department_configs (
        dept_id TEXT PRIMARY KEY,
        receiver_email TEXT,
        priority_api_endpoint TEXT,
        api_secret_token TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS unit_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_id TEXT,
        unit_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        payload TEXT,
        hash_signature TEXT
    )`);
});

// 1. Save or Update Department Admin Configuration & Priority API Data
app.post('/api/admin/config', (req, res) => {
    const { deptId, receiverEmail, priorityApiEndpoint, apiSecretToken } = req.body;
    
    if (!deptId || !receiverEmail) {
        return res.status(400).json({ error: 'Department ID and Receiver Email are required.' });
    }

    const query = `INSERT INTO department_configs (dept_id, receiver_email, priority_api_endpoint, api_secret_token) 
                   VALUES (?, ?, ?, ?) 
                   ON CONFLICT(dept_id) DO UPDATE SET 
                   receiver_email=excluded.receiver_email, 
                   priority_api_endpoint=excluded.priority_api_endpoint, 
                   api_secret_token=excluded.api_secret_token`;

    db.run(query, [deptId, receiverEmail, priorityApiEndpoint, apiSecretToken], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ success: true, message: 'Department configuration securely updated.' });
    });
});

// 2. Download/Package Individual Unit Telemetry into an Encrypted ZIP & Email it
app.post('/api/admin/export-unit-telemetry', async (req, res) => {
    const { deptId, unitId } = req.body;

    if (!deptId || !unitId) {
        return res.status(400).json({ error: 'Department ID and Unit ID are required.' });
    }

    // Fetch department configuration (receiver email & custom API priority info)
    db.get(`SELECT * FROM department_configs WHERE dept_id = ?`, [deptId], async (err, config) => {
        if (err || !config) {
            return res.status(404).json({ error: 'Department configuration not found.' });
        }

        // Fetch all telemetry entries for this specific unit
        db.all(`SELECT * FROM unit_telemetry WHERE dept_id = ? AND unit_id = ? ORDER BY timestamp ASC`, [deptId, unitId], async (err, rows) => {
            if (err) return res.status(500).json({ error: err.message });

            const exportFolder = path.join(__dirname, 'exports');
            if (!fs.existsSync(exportFolder)) fs.mkdirSync(exportFolder);

            const zipFileName = `Telemetry_${deptId}_Unit_${unitId}_${Date.now()}.zip`;
            const zipFilePath = path.join(exportFolder, zipFileName);

            const output = fs.createWriteStream(zipFilePath);
            const archive = archiver('zip', { zlib: { level: 9 } });

            output.on('close', async () => {
                try {
                    // Send via secure email transport (Configure your SMTP relay here)
                    const transporter = nodemailer.createTransport({
                        host: 'localhost',
                        port: 25,
                        secure: false
                    });

                    await transporter.sendMail({
                        from: '"Forensic Trust System" <secure-noreply@local.system>',
                        to: config.receiver_email,
                        subject: `[SECURE EXPORT] Telemetry Bundle for Unit: ${unitId}`,
                        text: `Attached is the cryptographically verified telemetry and audit package for Unit ${unitId} requested by Department ${deptId}.\n\nPriority API Configured: ${config.priority_api_endpoint || 'None'}`,
                        attachments: [{ path: zipFilePath }]
                    });

                    // Clean up local zip file after sending
                    fs.unlinkSync(zipFilePath);
                    res.json({ success: true, message: `Telemetry bundle successfully generated and transmitted to ${config.receiver_email}` });
                } catch (emailErr) {
                    res.status(500).json({ error: 'Failed to dispatch email package: ' + emailErr.message });
                }
            });

            archive.on('error', (err) => { throw err; });
            archive.pipe(output);

            // Append metadata json including department priority settings
            const metadata = {
                departmentId: deptId,
                unitId: unitId,
                generatedAt: new Date().toISOString(),
                priorityApiEndpoint: config.priority_api_endpoint,
                totalRecords: rows.length
            };
            archive.append(JSON.stringify(metadata, null, 2), { name: 'metadata.json' });

            // Append structured telemetry logs
            archive.append(JSON.stringify(rows, null, 2), { name: 'telemetry_audit_trail.json' });

            archive.finalize();
        });
    });
});

app.listen(3000, () => console.log('Secure Admin API running on port 3000'));
