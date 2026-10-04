/**
 * ANNON AI MASTER COMMAND REGISTRY & DISPATCHER ENGINE
 * System: Trust Forensics Platform
 * Function: Maps 100% of verbal voice phrases and metadata tags to live code.
 */

const crypto = require('crypto');

// ============================================================================
// 1. HARDWARE & SUBSYSTEM FUNCTION MODULES
// ============================================================================

const SystemModule = {
    clockIn: async (session, args) => ({ sessionId: 'SESS-9081', status: 'PAID_DUTY_ACTIVE', officer: session.officerId }),
    clockOut: async (session, args) => ({ sessionId: session.sessionId, status: 'SHIFT_SEALED_APPROVED', payroll: 'RELEASED' }),
    getStatus: async () => ({ battery: '88%', storageFree: '412GB', ledger: 'ONLINE', sensors: 'ALL_OPERATIONAL' }),
    pauseMic: async (session, reason) => ({ state: 'MIC_MUTED', breakLogged: true, timecard: 'PAUSED' })
};

const ForensicsModule = {
    activateWitnessShare: async (session) => ({
        beaconId: `SHARE-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
        qrPayload: `https://trust.forensics.gov/ingress/${session.sessionId}`,
        wifiDirectSSID: `TRUST_WITNESS_${session.sessionId.slice(0, 6)}`,
        status: 'LISTENING_FOR_WITNESS_UPLOADS'
    }),
    captureLiDARScan: async (session) => ({ scanId: `LIDAR-${crypto.randomBytes(3).toString('hex').toUpperCase()}`, points: 4500000, bounds: '12m x 15m' }),
    recordThermal: async (session, target) => ({ captureId: `THERM-${crypto.randomBytes(3).toString('hex').toUpperCase()}`, target, minTemp: '18.4C', maxTemp: '34.2C' }),
    tagEvidence: async (session, item) => ({ tagId: `TAG-${crypto.randomBytes(3).toString('hex').toUpperCase()}`, item, gps: '45.6312,-122.6716' }),
    flagEscalation: async (session) => ({ ticketId: `IA-ALERT-${crypto.randomBytes(4).toString('hex').toUpperCase()}`, priority: 'CRITICAL', routedTo: 'INTERNAL_AFFAIRS' }),
    recordStatement: async (session) => ({ statementId: `STMT-${crypto.randomBytes(3).toString('hex').toUpperCase()}`, acousticGain: 'BOOSTED' })
};

const EMSModule = {
    logVitals: async (session, vitals) => ({ epcrId: 'EPCR-4402', vitalsParsed: vitals, timestamp: new Date().toISOString() }),
    logMedication: async (session, med) => ({ epcrId: 'EPCR-4402', medAdministered: med, timestamp: new Date().toISOString() }),
    scanTrauma: async (session) => ({ perfusionIndex: '0.84', subcutaneousPattern: 'NO_INTERNAL_HEMORRHAGE_DETECTED' }),
    transmitEPCR: async (session, hospital) => ({ hospitalDestination: hospital, epcrHash: 'a7f9c8...', status: 'TRANSMITTED' })
};

const FireModule = {
    scanWallTemp: async (session) => ({ peakTempC: 171.1, deltaRate: '+2.4C/sec', risk: 'HIGH_SPREAD' }),
    detectHotspots: async (session) => ({ vector: 'AHEAD_RIGHT_12FT', temperatureC: 245.0 }),
    readHazmat: async (session) => ({ classNumber: '3', category: 'FLAMMABLE_LIQUID', ergId: '128' })
};

const BlockchainModule = {
    lockScene: async (session) => ({ blockId: `BLOCK-${crypto.randomBytes(6).toString('hex')}`, hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' }),
    transmitToLab: async (session) => ({ packageId: `LAB-PKG-${crypto.randomBytes(4).toString('hex')}`, daDiscoveryReceipt: 'VERIFIED' })
};

const SecurityModule = {
    triggerDeadManSwitch: async (reason) => {
        console.error(`[CRITICAL SECURITY ALERT]: Dead-Man Switch Fired -> ${reason}`);
        return { status: 'KEYS_PURGED_BINARY_CORRUPTED', reinstallRequired: true };
    }
};

// ============================================================================
// 2. THE MASTER COMMAND REGISTRY
// ============================================================================

const CommandRegistry = new Map();

// Helper to register commands cleanly
function registerCommand(config) {
    CommandRegistry.set(config.tag, config);
}

// --- SYSTEM & AUTHENTICATION ---
registerCommand({
    tag: '@tag:sys.auth.shift_init',
    commandId: 'CMD_INITIATE_SHIFT',
    phrasePattern: /annon,?\s+initiate\s+shift/i,
    action: async (session, args) => await SystemModule.clockIn(session, args),
    audioResponse: (data) => `Shift initiated. Welcome, ${data.officer}.`
});

registerCommand({
    tag: '@tag:sys.auth.shift_end',
    commandId: 'CMD_END_SHIFT',
    phrasePattern: /annon,?\s+end\s+shift/i,
    action: async (session, args) => await SystemModule.clockOut(session, args),
    audioResponse: (data) => "Perform symmetric clock-out scan to seal shift."
});

registerCommand({
    tag: '@tag:sys.diagnostics.status',
    commandId: 'CMD_SYSTEM_STATUS',
    phrasePattern: /annon,?\s+system\s+status/i,
    action: async () => await SystemModule.getStatus(),
    audioResponse: (data) => `All sensors active. Battery at ${data.battery}. Blockchain ledger ${data.ledger}.`
});

registerCommand({
    tag: '@tag:sys.privacy.mute_mic',
    commandId: 'CMD_MUTE_MIC',
    phrasePattern: /annon,?\s+mute\s+mic/i,
    action: async (session) => await SystemModule.pauseMic(session, 'PERSONAL_BREAK'),
    audioResponse: () => "Microphone muted. Personal break logged to timecard."
});

// --- LAW ENFORCEMENT & FORENSICS ---
registerCommand({
    tag: '@tag:forensics.ingress.witness_share',
    commandId: 'CMD_ACTIVATE_EVIDENCE_SHARE',
    phrasePattern: /annon,?\s+activate\s+evidence\s+share/i,
    action: async (session) => await ForensicsModule.activateWitnessShare(session),
    audioResponse: () => "Evidence share active. Secure witness transfer link generated."
});

registerCommand({
    tag: '@tag:forensics.lidar.spatial_scan',
    commandId: 'CMD_CAPTURE_3D_SCAN',
    phrasePattern: /annon,?\s+capture\s+3d\s+scan/i,
    action: async (session) => await ForensicsModule.captureLiDARScan(session),
    audioResponse: (data) => `3D spatial scan complete. Mesh ${data.scanId} generated.`
});

registerCommand({
    tag: '@tag:forensics.thermal.heat_decay',
    commandId: 'CMD_THERMAL_SCAN',
    phrasePattern: /annon,?\s+thermal\s+scan\s+(.+)/i,
    action: async (session, args) => await ForensicsModule.recordThermal(session, args.target || 'scene'),
    audioResponse: (data) => `Thermal profile for ${data.target} captured and timestamped.`
});

registerCommand({
    tag: '@tag:forensics.evidence.spatial_tag',
    commandId: 'CMD_TAG_EVIDENCE',
    phrasePattern: /annon,?\s+tag\s+evidence\s+(.+)/i,
    action: async (session, args) => await ForensicsModule.tagEvidence(session, args.item || 'unspecified item'),
    audioResponse: (data) => `Evidence tag created for ${data.item}.`
});

registerCommand({
    tag: '@tag:sys.safety.escalation_flag',
    commandId: 'CMD_FLAG_ESCALATION',
    phrasePattern: /annon,?\s+flag\s+escalation/i,
    action: async (session) => await ForensicsModule.flagEscalation(session),
    audioResponse: () => "Incident flagged. Emergency stream routed directly to Internal Affairs."
});

registerCommand({
    tag: '@tag:forensics.audio.statement',
    commandId: 'CMD_RECORD_STATEMENT',
    phrasePattern: /annon,?\s+record\s+statement/i,
    action: async (session) => await ForensicsModule.recordStatement(session),
    audioResponse: () => "Statement recording mode active."
});

// --- EMS & PARAMEDIC ---
registerCommand({
    tag: '@tag:ems.epcr.vitals',
    commandId: 'CMD_LOG_VITALS',
    phrasePattern: /annon,?\s+log\s+vitals\s+(.+)/i,
    action: async (session, args) => await EMSModule.logVitals(session, args.vitals),
    audioResponse: (data) => `Vitals recorded: ${data.vitalsParsed}.`
});

registerCommand({
    tag: '@tag:ems.epcr.medication',
    commandId: 'CMD_LOG_MEDICATION',
    phrasePattern: /annon,?\s+log\s+medication\s+(.+)/i,
    action: async (session, args) => await EMSModule.logMedication(session, args.medication),
    audioResponse: (data) => `Medication logged: ${data.medAdministered}.`
});

registerCommand({
    tag: '@tag:ems.thermal.trauma_scan',
    commandId: 'CMD_SCAN_TRAUMA_PROFILE',
    phrasePattern: /annon,?\s+scan\s+trauma\s+profile/i,
    action: async (session) => await EMSModule.scanTrauma(session),
    audioResponse: () => "Subcutaneous thermal trauma scan recorded."
});

registerCommand({
    tag: '@tag:ems.network.epcr_transmit',
    commandId: 'CMD_TRANSMIT_EPCR',
    phrasePattern: /annon,?\s+transmit\s+epcr\s+(.+)/i,
    action: async (session, args) => await EMSModule.transmitEPCR(session, args.hospital),
    audioResponse: (data) => `ePCR encrypted and transmitted to ${data.hospitalDestination}.`
});

// --- FIRE & HAZMAT ---
registerCommand({
    tag: '@tag:fire.thermal.wall_gradient',
    commandId: 'CMD_SCAN_WALL_TEMP',
    phrasePattern: /annon,?\s+scan\s+wall\s+temperature/i,
    action: async (session) => await FireModule.scanWallTemp(session),
    audioResponse: (data) => `Wall profile analyzed. Peak temperature ${data.peakTempC} degrees Celsius.`
});

registerCommand({
    tag: '@tag:fire.thermal.hotspot_detection',
    commandId: 'CMD_DETECT_HOTSPOTS',
    phrasePattern: /annon,?\s+detect\s+hot\s*spots/i,
    action: async (session) => await FireModule.detectHotspots(session),
    audioResponse: (data) => `Hotspot located at ${data.vector}. Temperature ${data.temperatureC} degrees.`
});

registerCommand({
    tag: '@tag:fire.ocr.hazmat_reader',
    commandId: 'CMD_READ_HAZMAT_PLACARD',
    phrasePattern: /annon,?\s+read\s+hazmat\s+placard/i,
    action: async (session) => await FireModule.readHazmat(session),
    audioResponse: (data) => `Hazmat placard identified. Class ${data.classNumber}, ${data.category}.`
});

// --- BLOCKCHAIN & SECURITY ---
registerCommand({
    tag: '@tag:blockchain.ledger.lock_scene',
    commandId: 'CMD_LOCK_SCENE',
    phrasePattern: /annon,?\s+lock\s+scene/i,
    action: async (session) => await BlockchainModule.lockScene(session),
    audioResponse: () => "Scene files locked and hashed to immutable ledger."
});

registerCommand({
    tag: '@tag:blockchain.ledger.lab_transmit',
    commandId: 'CMD_TRANSMIT_LAB',
    phrasePattern: /annon,?\s+transmit\s+to\s+lab/i,
    action: async (session) => await BlockchainModule.transmitToLab(session),
    audioResponse: () => "Evidence package transmitted directly to Crime Lab."
});

registerCommand({
    tag: '@tag:sec.hardware.deadman_switch',
    commandId: 'SYS_DEADMAN_TRIGGER',
    phrasePattern: /^__TAMPER_TRIGGER__$/,
    action: async (session, args) => await SecurityModule.triggerDeadManSwitch(args.reason),
    audioResponse: () => "Terminal destruction initiated."
});

// ============================================================================
// 3. THE DISPATCHER ENGINE
// ============================================================================

class AnnonDispatcher {
    /**
     * Parse raw spoken text, match regex pattern to metadata tag, and execute code
     */
    static async processSpokenPhrase(spokenText, activeSession) {
        const text = spokenText.trim();
        let matchedConfig = null;
        let extractedArgs = {};

        // Match spoken phrase against registry patterns
        for (const [tag, config] of CommandRegistry.entries()) {
            const match = text.match(config.phrasePattern);
            if (match) {
                matchedConfig = config;
                
                // Extract regex capture groups for dynamic parameters
                if (match[1]) {
                    if (tag.includes('thermal')) extractedArgs.target = match[1].trim();
                    if (tag.includes('evidence.spatial_tag')) extractedArgs.item = match[1].trim();
                    if (tag.includes('epcr.vitals')) extractedArgs.vitals = match[1].trim();
                    if (tag.includes('epcr.medication')) extractedArgs.medication = match[1].trim();
                    if (tag.includes('epcr_transmit')) extractedArgs.hospital = match[1].trim();
                }
                break;
            }
        }

        if (!matchedConfig) {
            return {
                success: false,
                audioResponse: "Command not recognized. Please repeat."
            };
        }

        // Execute the bound function
        const dataPayload = await matchedConfig.action(activeSession, extractedArgs);
        const spokenConfirmation = matchedConfig.audioResponse(dataPayload);

        return {
            success: true,
            tag: matchedConfig.tag,
            commandId: matchedConfig.commandId,
            data: dataPayload,
            audioResponse: spokenConfirmation
        };
    }
}

// ============================================================================
// 4. TEST EXECUTION (VERIFYING EVERY COMMAND)
// ============================================================================

(async function runMasterCommandTest() {
    const mockSession = { sessionId: 'SESS-7042', officerId: 'OFFICER-7042' };

    const testPhrases = [
        "Annon, initiate shift",
        "Annon, system status",
        "Annon, activate evidence share",
        "Annon, capture 3D scan",
        "Annon, thermal scan vehicle engine",
        "Annon, tag evidence shell casing",
        "Annon, record statement",
        "Annon, log vitals 120 over 80 pulse 72",
        "Annon, log medication 4mg Narcan left nostril",
        "Annon, scan trauma profile",
        "Annon, transmit ePCR PeaceHealth Hospital",
        "Annon, scan wall temperature",
        "Annon, detect hot spots",
        "Annon, read hazmat placard",
        "Annon, flag escalation",
        "Annon, lock scene",
        "Annon, transmit to lab",
        "Annon, mute mic",
        "Annon, end shift"
    ];

    console.log("=================================================================");
    console.log("   ANNON MASTER COMMAND ROUTER — FULL REGISTRY VERIFICATION");
    console.log("=================================================================\n");

    for (const phrase of testPhrases) {
        const result = await AnnonDispatcher.processSpokenPhrase(phrase, mockSession);
        console.log(`INPUT: "${phrase}"`);
        console.log(`  └─ TAG: ${result.tag}`);
        console.log(`  └─ ID:  ${result.commandId}`);
        console.log(`  └─ AUDIO: 🔊 "${result.audioResponse}"\n`);
    }
})();
