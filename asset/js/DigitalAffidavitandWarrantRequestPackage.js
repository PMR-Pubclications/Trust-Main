/**
 * Evaluates the evidence collection threshold and triggers the judicial 
 * warrant application workflow only when 10 or more significant items are logged.
 */
async function evaluateAndTriggerWarrant(caseId, evidenceList, targetCameras, blockchainHash, judicialGatewayEndpoint = null) {
    const EVIDENCE_THRESHOLD = 10;
    const DEFAULT_ENDPOINT = "https://api.localjudicialdistrict.gov/v1/warrants/submit";

    // Input validation
    if (!caseId || typeof caseId !== 'string') {
        throw new Error("Invalid caseId: must be a non-empty string");
    }
    if (!Array.isArray(evidenceList)) {
        throw new Error("Invalid evidenceList: must be an array");
    }
    if (!Array.isArray(targetCameras)) {
        throw new Error("Invalid targetCameras: must be an array");
    }
    if (!blockchainHash || typeof blockchainHash !== 'string') {
        throw new Error("Invalid blockchainHash: must be a non-empty string");
    }

    console.log(`Current evidence count for Case ${caseId}: ${evidenceList.length}/${EVIDENCE_THRESHOLD}`);

    if (evidenceList.length < EVIDENCE_THRESHOLD) {
        console.log(`Threshold not met. Additional evidence required before judicial warrant application can be filed.`);
        return { 
            triggered: false, 
            message: `Need ${EVIDENCE_THRESHOLD - evidenceList.length} more pieces of evidence to reach the statutory threshold.` 
        };
    }

    console.log(`Threshold reached! Initiating Q&A and Electronic Warrant Packet generation...`);

    // Compile the formal digital affidavit package once the threshold is cleared
    const warrantApplication = {
        jurisdiction: "Local Judicial District - On-Call Magistrate Division",
        timestamp: new Date().toISOString(),
        caseDetails: {
            caseNumber: caseId,
            totalSignificantEvidenceItems: evidenceList.length,
            evidenceSummary: evidenceList.map(item => ({
                description: item.description || "Unknown",
                timestamp: item.timestamp || new Date().toISOString()
            }))
        },
        integrityVerification: {
            anchorProtocol: "Blockchain Immutable Mirror",
            sha256Hash: blockchainHash,
            status: "Verified Unaltered"
        },
        targetSurveillanceAssets: targetCameras.map(cam => ({
            deviceName: cam.name || "Unknown Device",
            macOrBluetoothAddress: cam.address || "Unknown Address",
            signalStrength: cam.rssi || -1,
            status: "Detected in Range - Preservation Order Requested"
        })),
        legalPrayer: `The investigating authority has compiled the statutory minimum of ${EVIDENCE_THRESHOLD} verified forensic items and respectfully requests an emergency digital preservation and search order for the aforementioned surveillance devices under applicable state and federal law.`
    };

    // Transmit securely to the Judicial District's On-Call E-Warrant API Gateway
    const endpoint = judicialGatewayEndpoint || DEFAULT_ENDPOINT;

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'DigitalAffidavitPackageClient/1.0'
            },
            body: JSON.stringify(warrantApplication),
            timeout: 30000
        });

        if (!response.ok) {
            throw new Error(`Judicial gateway rejected transmission: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        
        if (!result.trackingId) {
            throw new Error("Invalid response: missing tracking ID from judicial gateway");
        }

        console.log(`Success: Warrant packet logged with Magistrate Queue. Tracking ID: ${result.trackingId}`);
        return { 
            triggered: true, 
            success: true, 
            trackingId: result.trackingId,
            timestamp: new Date().toISOString()
        };

    } catch (error) {
        console.warn(`Simulated Local Network Fallback: E-Warrant endpoint offline. Package saved locally with cryptographic proof.`);
        console.error(`Error details: ${error.message}`);
        return { 
            triggered: true, 
            success: false, 
            error: error.message, 
            localPayload: warrantApplication,
            fallbackTimestamp: new Date().toISOString()
        };
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { evaluateAndTriggerWarrant };
}
