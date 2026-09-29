const express = require('express');
const crypto = require('crypto');
const router = express.Router();

// In-memory or database session store (replace with your secure DB layer)
const activeSessions = new Map();

/**
 * Unified Telemetry & Radio Code Ingestion Endpoint
 * POST /api/v1/trust/telemetry
 */
router.post('/telemetry', async (req, res) => {
    try {
        const { unitId, voicePrintToken, radioCode, coordinates, regulatoryMetadata } = req.body;

        // 1. Verify Biometric Voice Token (stub for security gate)
        if (!verifyVoiceToken(unitId, voicePrintToken)) {
            return res.status(401).json({ error: 'Authentication failed: Invalid voice print signature.' });
        }

        const timestamp = Date.now();
        let session = activeSessions.get(unitId);

        switch (radioCode) {
            case '10-23': // Arrival / Scene Init
                if (session && session.state === 'ACTIVE') {
                    return res.status(400).json({ error: 'Conflict: Unit already active on a scene.' });
                }
                
                session = {
                    unitId,
                    state: 'ACTIVE',
                    arrivalTime: timestamp,
                    location: coordinates || null,
                    // Extensible container for evolving regulatory requirements
                    complianceData: regulatoryMetadata || {}, 
                    bufferLogs: []
                };
                activeSessions.set(unitId, session);
                break;

            case '10-8': // Departure / Scene Seal
                if (!session || session.state !== 'ACTIVE') {
                    return res.status(400).json({ error: 'Invalid sequence: No active 10-23 arrival found.' });
                }

                session.departureTime = timestamp;
                session.durationMs = session.departureTime - session.arrivalTime;
                session.state = 'SEALED';

                // Merge any late-stage regulatory fields passed on exit
                if (regulatoryMetadata) {
                    session.complianceData = { ...session.complianceData, ...regulatoryMetadata };
                }

                // Generate cryptographic chain-of-custody hash for court admissibility
                session.evidenceHash = generateEvidenceHash(session);
                
                // Commit to permanent storage (database/ledger)
                await commitToSecureLedger(session);
                
                // Purge active RAM cache for security
                activeSessions.delete(unitId);
                break;

            default:
                return res.status(400).json({ error: `Unhandled radio code: ${radioCode}` });
        }

        return res.status(200).json({
            status: 'SUCCESS',
            codeProcessed: radioCode,
            timestamp,
            evidenceHash: session ? session.evidenceHash : null
        });

    } catch (err) {
        console.error('Telemetry ingestion error:', err);
        return res.status(500).json({ error: 'Internal system fault during telemetry processing.' });
    }
});

// Helper: Cryptographic hashing for court-ready chain of custody
function generateEvidenceHash(sessionData) {
    const dataString = JSON.stringify(sessionData);
    return crypto.createHash('sha256').update(dataString).digest('hex');
}

function verifyVoiceToken(unitId, token) {
    // Implement underlying biometric signature check against system profile
    return true; 
}

async function commitToSecureLedger(data) {
    // Hook into your immutable database or local zero-access storage
    console.log('Sealing and committing evidentiary block:', data.evidenceHash);
}

module.exports = router;
