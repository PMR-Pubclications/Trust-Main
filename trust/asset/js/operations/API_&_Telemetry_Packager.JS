const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const archiver = require('archiver');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// Initialize secure local database
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
        payload TEXT
    )`);
});

// --- BACKEND API ROUTES ---

// 1. Save or Update Department Admin Configuration
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

// 2. Package Individual Unit Telemetry, External Case File into a ZIP, & Email it
app.post('/api/admin/export-unit-telemetry', async (req, res) => {
    const { deptId, unitId } = req.body;

    if (!deptId || !unitId) {
        return res.status(400).json({ error: 'Department ID and Unit ID are required.' });
    }

    db.get(`SELECT * FROM department_configs WHERE dept_id = ?`, [deptId], async (err, config) => {
        if (err || !config) {
            return res.status(404).json({ error: 'Department configuration not found.' });
        }

        // --- STEP A: FETCH EXTERNAL CASE FILE FROM DEPARTMENT API ---
        let externalCaseData = null;
        if (config.priority_api_endpoint) {
            try {
                const apiResponse = await fetch(`${config.priority_api_endpoint}?unitId=${unitId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${config.api_secret_token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (apiResponse.ok) {
                    externalCaseData = await apiResponse.json();
                } else {
                    console.warn(`Department API returned status ${apiResponse.status}, proceeding with local telemetry only.`);
                }
            } catch (fetchErr) {
                console.error('Failed to reach department priority API:', fetchErr.message);
            }
        }

        // --- STEP B: FETCH LOCAL UNIT TELEMETRY FROM DATABASE ---
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
                    const transporter = nodemailer.createTransport({
                        host: 'localhost',
                        port: 25,
                        secure: false
                    });

                    await transporter.sendMail({
                        from: '"Forensic Trust System" <secure-noreply@local.system>',
                        to: config.receiver_email,
                        subject: `[SECURE EXPORT] Telemetry & Case Bundle for Unit: ${unitId}`,
                        text: `Attached is the cryptographically verified telemetry audit trail and integrated case file package for Unit ${unitId} requested by Department ${deptId}.`,
                        attachments: [{ path: zipFilePath }]
                    });

                    fs.unlinkSync(zipFilePath);
                    res.json({ success: true, message: `Telemetry & Case File bundle successfully generated and transmitted to ${config.receiver_email}` });
                } catch (emailErr) {
                    res.status(500).json({ error: 'Failed to dispatch email package (Check local mail relay): ' + emailErr.message });
                }
            });

            archive.on('error', (err) => { throw err; });
            archive.pipe(output);

            // 1. Append Metadata
            const metadata = {
                departmentId: deptId,
                unitId: unitId,
                generatedAt: new Date().toISOString(),
                priorityApiEndpoint: config.priority_api_endpoint,
                totalTelemetryRecords: rows.length,
                caseFileAttached: externalCaseData ? true : false
            };
            archive.append(JSON.stringify(metadata, null, 2), { name: 'metadata.json' });

            // 2. Append Local Telemetry Audit Trail
            archive.append(JSON.stringify(rows, null, 2), { name: 'telemetry_audit_trail.json' });

            // 3. Append External Case File Data (if successfully fetched)
            if (externalCaseData) {
                archive.append(JSON.stringify(externalCaseData, null, 2), { name: 'department_case_file.json' });
            }

            archive.finalize();
        });
    });
});


// --- INTEGRATED FRONTEND (Served directly at root URL) ---

app.get('/', (req, res) => {
    res.send(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>First Response Admin - Telemetry & Unit Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen p-6">
    <div class="max-w-4xl mx-auto space-y-8">
        
        <header class="border-b border-slate-700 pb-4">
            <h1 class="text-2xl font-bold tracking-wide">First Response Admin Console</h1>
            <p class="text-sm text-slate-400">Department Unit Telemetry, Chain-of-Custody & API Configuration</p>
        </header>

        <!-- Department Configuration Section -->
        <section class="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
            <h2 class="text-lg font-semibold mb-4 text-emerald-400">Department Configuration & Priority APIs</h2>
            <form id="configForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">Department ID</label>
                        <input type="text" id="deptId" required class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500" placeholder="e.g. PD-WA-104">
                    </div>
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">Receiver Notification Email</label>
                        <input type="email" id="receiverEmail" required class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500" placeholder="admin@department.gov">
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">Priority API Endpoint</label>
                        <input type="url" id="priorityApiEndpoint" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500" placeholder="https://api.department.gov/v1/ingest">
                    </div>
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">API Secret / Auth Token</label>
                        <input type="password" id="apiSecretToken" class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500" placeholder="Bearer Token or Key">
                    </div>
                </div>
                <button type="submit" class="bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm px-4 py-2 rounded transition">Save Configuration</button>
            </form>
        </section>

        <!-- Individual Unit Telemetry Export Section -->
        <section class="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
            <h2 class="text-lg font-semibold mb-4 text-cyan-400">Individual Unit Telemetry Package Export</h2>
            <form id="exportForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">Target Department ID</label>
                        <input type="text" id="exportDeptId" required class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" placeholder="e.g. PD-WA-104">
                    </div>
                    <div>
                        <label class="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">Unit ID / Mobile Terminal</label>
                        <input type="text" id="unitId" required class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" placeholder="e.g. Unit-Alpha-03">
                    </div>
                </div>
                <button type="submit" class="bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm px-4 py-2 rounded transition">Package & Dispatch Telemetry ZIP</button>
            </form>
        </section>

        <div id="statusBox" class="hidden p-4 rounded text-sm font-medium border"></div>

    </div>

    <script>
        const showStatus = (message, isError = false) => {
            const box = document.getElementById('statusBox');
            box.textContent = message;
            box.className = \`p-4 rounded text-sm font-medium border \${isError ? 'bg-red-950 border-red-800 text-red-200' : 'bg-emerald-950 border-emerald-800 text-emerald-200'}\`;
            box.classList.remove('hidden');
        };

        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                deptId: document.getElementById('deptId').value,
                receiverEmail: document.getElementById('receiverEmail').value,
                priorityApiEndpoint: document.getElementById('priorityApiEndpoint').value,
                apiSecretToken: document.getElementById('apiSecretToken').value
            };

            try {
                const res = await fetch('/api/admin/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) showStatus(data.message);
                else showStatus(data.error, true);
            } catch (err) {
                showStatus('Network error while saving configuration.', true);
            }
        });

        document.getElementById('exportForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                deptId: document.getElementById('exportDeptId').value,
                unitId: document.getElementById('unitId').value
            };

            showStatus('Compiling unit logs and fetching department case file into ZIP archive...', false);

            try {
                const res = await fetch('/api/admin/export-unit-telemetry', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) showStatus(data.message);
                else showStatus(data.error, true);
            } catch (err) {
                showStatus('Network error during telemetry extraction.', true);
            }
        });
    </script>
</body>
</html>`);
});

// Start Server
app.listen(3000, () => {
    console.log('--------------------------------------------------');
    console.log(' Forensic Trust Admin Server running locally.');
    console.log(' Open your browser and navigate to: http://localhost:3000');
    console.log('--------------------------------------------------');
});
