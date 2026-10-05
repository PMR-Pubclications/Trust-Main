// Trust-Main/lib/initDb.js
const fs = require('fs');
const path = require('path');
const db = require('../db');

async function initializeDevicesTable() {
    try {
        // Explicitly using the singular 'asset' directory
        const sqlPath = path.join(__dirname, '..', 'asset', 'SQL', 'devicesTable.sql');
        
        if (!fs.existsSync(sqlPath)) {
            console.error(`[TRUST-MAIN] Schema file missing at: ${sqlPath}`);
            return;
        }

        const sqlSchema = fs.readFileSync(sqlPath, 'utf8');
        await db.query(sqlSchema);
        console.log('[TRUST-MAIN] Database schema initialized from asset/SQL/devicesTable.sql');
    } catch (err) {
        console.error('[TRUST-MAIN] Failed to initialize devices table schema:', err);
        throw err;
    }
}

module.exports = { initializeDevicesTable };
