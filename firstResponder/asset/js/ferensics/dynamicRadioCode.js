const express = require('express');
const router = express.Router();

// Simulated database wrapper (replace with your persistent SQL/NoSQL DB)
let radioCodeRegistry = new Map([
    ['NATIONAL_APCO:10-23', { meaning: 'Arrived at Scene', action: 'OPS_UNIT_ARRIVAL' }],
    ['NATIONAL_APCO:10-8', { meaning: 'In Service / Leaving Scene', action: 'OPS_UNIT_DEPARTURE' }],
    ['NATIONAL_APCO:10-70', { meaning: 'Fire Alarm / Fire Report', action: 'OPS_FIRE_INCIDENT' }]
]);

/**
 * 1. SYNC / UPSERT RADIO CODE MATRIX
 * POST /api/v1/trust/codes/sync
 * Allows the client app to push batch or single code updates for specific jurisdictions.
 */
router.post('/codes/sync', async (req, res) => {
    try {
        const { agencyId, codes } = req.body; 
        // Expected format: codes = [{ code: "10-23", meaning: "Custom Desc", action: "OPS_UNIT_ARRIVAL" }, ...]

        if (!agencyId || !Array.isArray(codes)) {
            return res.status(400).json({ error: 'Invalid payload structure. Provide agencyId and codes array.' });
        }

        let updatedCount = 0;
        for (const entry of codes) {
            const registryKey = `${agencyId}:${entry.code}`;
            radioCodeRegistry.set(registryKey, {
                meaning: entry.meaning,
                action: entry.action || 'CUSTOM_LOG_EVENT',
                updatedAt: new Date().toISOString()
            });
            updatedCount++;
        }

        return res.status(200).json({
            status: 'SUCCESS',
            message: `Successfully synchronized ${updatedCount} codes for agency: ${agencyId}`
        });

    } catch (err) {
        console.error('Code synchronization fault:', err);
        return res.status(500).json({ error: 'Failed to update radio code database.' });
    }
});

/**
 * 2. RESOLVE CODE DURING VOICE PARSING
 * GET /api/v1/trust/codes/resolve?agency=WASH_PD_402&code=10-23
 * Falls back to NATIONAL_APCO if local agency override doesn't exist.
 */
router.get('/codes/resolve', (req, res) => {
    const { agency, code } = req.query;

    if (!code) {
        return res.status(400).json({ error: 'Missing code parameter.' });
    }

    // Check agency-specific override first, then fall back to national standard
    let resolvedData = radioCodeRegistry.get(`${agency}:${code}`) || radioCodeRegistry.get(`NATIONAL_APCO:${code}`);

    if (!resolvedData) {
        return res.status(404).json({ error: `Radio code ${code} not recognized for agency or national baseline.` });
    }

    return res.status(200).json({
        code,
        agency: agency || 'NATIONAL_APCO',
        ...resolvedData
    });
});

module.exports = router;
