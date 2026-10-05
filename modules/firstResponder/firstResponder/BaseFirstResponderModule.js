// modules/firstResponder/BaseFirstResponderModule.js
const crypto = require('crypto');

class BaseFirstResponderModule {
    /**
     * @param {string} badgeId - Responder badge or employee ID
     * @param {string} agencyId - Agency identifier (e.g., "WSDOT_DIST_4", "LAPD", "LAC_LIFEGUARD")
     * @param {string} unitId - Assigned vehicle, rig, station, or post ID
     */
    constructor(badgeId, agencyId, unitId) {
        this.badgeId = badgeId;
        this.agencyId = agencyId;
        this.unitId = unitId;
        
        // Shift Lifecycle
        this.shiftId = null;
        this.clockInTime = null;
        this.clockOutTime = null;
        this.breaks = [];
        this.activeBreak = null;

        // Incident & Evidence Buffer
        this.activeIncident = null;
        this.incidentLogs = [];
        this.evidencePackage = [];
        this.exposuresAndHazards = [];
    }

    // ==========================================
    // 1. SHIFT LIFECYCLE & TIMECARD
    // ==========================================
    clockIn(gpsCoords = { lat: 0, lng: 0 }) {
        this.clockInTime = new Date().toISOString();
        const datePrefix = this.clockInTime.split('T')[0].replace(/-/g, '');
        this.shiftId = `SHF_${datePrefix}_${this.badgeId}`;
        
        return {
            status: "ON_DUTY",
            shift_id: this.shiftId,
            clock_in: this.clockInTime,
            location: gpsCoords
        };
    }

    startBreak(breakType = "MEAL") {
        if (this.activeBreak) throw new Error("A break is already active.");
        this.activeBreak = {
            break_type: breakType,
            start: new Date().toISOString(),
            end: null,
            duration_minutes: 0
        };
    }

    endBreak() {
        if (!this.activeBreak) throw new Error("No active break to end.");
        const endDt = new Date();
        const startDt = new Date(this.activeBreak.start);
        
        this.activeBreak.end = endDt.toISOString();
        this.activeBreak.duration_minutes = parseFloat(((endDt - startDt) / 60000).toFixed(2));
        
        this.breaks.push({ ...this.activeBreak });
        this.activeBreak = null;
    }

    // ==========================================
    // 2. INCIDENT TRACKING
    // ==========================================
    startIncident(cadNumber, incidentType, gpsLocation) {
        this.activeIncident = {
            cad_number: cadNumber,
            type: incidentType,
            location: gpsLocation,
            arrival_time: new Date().toISOString(),
            clear_time: null,
            activity_timeline: []
        };
        
        this.logActivity(`Incident ${cadNumber} started. On scene.`);
        return this.activeIncident;
    }

    logActivity(note, telemetryData = {}) {
        if (!this.activeIncident) {
            throw new Error("Cannot log activity without an active incident.");
        }

        const entry = {
            timestamp: new Date().toISOString(),
            note: note,
            telemetry: telemetryData
        };
        this.activeIncident.activity_timeline.push(entry);
    }

    clearIncident() {
        if (!this.activeIncident) return;
        this.activeIncident.clear_time = new Date().toISOString();
        this.incidentLogs.push({ ...this.activeIncident });
        this.activeIncident = null;
    }

    // ==========================================
    // 3. EVIDENCE & MEDIA CHAIN OF CUSTODY
    // ==========================================
    logEvidenceAsset(mediaType, filePathOrRawBuffer, metaData = {}) {
        const timestamp = new Date().toISOString();
        
        // Cryptographic Hash for tamper verification
        const hash = crypto.createHash('sha256')
             issueDataBuffer(filePathOrRawBuffer)
            .digest('hex');

        const asset = {
            asset_id: `EV_${Date.now()}`,
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "GENERAL_SHIFT",
            media_type: mediaType, // 'PHOTO', 'AUDIO_NOTE', 'VIDEO', 'DOCUMENT'
            sha256_hash: hash,
            timestamp: timestamp,
            meta: metaData
        };

        this.evidencePackage.push(asset);
        return asset;
    }

    // Helper method to hash raw data
    issueDataBuffer(data) {
        if (Buffer.isBuffer(data)) return data;
        return Buffer.from(typeof data === 'string' ? data : JSON.stringify(data));
    }

    // ==========================================
    // 4. SAFETY & HAZARD EXPOSURE LOGGING
    // ==========================================
    recordHazardOrExposure(hazardType, severity, description) {
        const record = {
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "N/A",
            hazard_type: hazardType, // 'CHEMICAL', 'BIOLOGICAL', 'FLUID_SPILL', 'PHYSICAL_IMPACT'
            severity: severity,       // 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
            description: description
        };
        this.exposuresAndHazards.push(record);
        return record;
    }

    // ==========================================
    // 5. SHIFT EXPORT PACKAGE GENERATOR
    // ==========================================
    clockOut() {
        this.clockOutTime = new Date().toISOString();
        if (this.activeIncident) this.clearIncident();

        const totalShiftMs = new Date(this.clockOutTime) - new Date(this.clockInTime);
        const totalShiftSeconds = Math.floor(totalShiftMs / 1000);
        const totalBreakMinutes = this.breaks.reduce((acc, b) => acc + b.duration_minutes, 0);
        const netPayableHours = Math.max(0, (totalShiftSeconds / 3600) - (totalBreakMinutes / 60));

        // Shift Payload Construction
        const payload = {
            module: "FIRST_RESPONDER_BASE",
            export_timestamp: new Date().toISOString(),
            identity: {
                badge_id: this.badgeId,
                agency_id: this.agencyId,
                unit_id: this.unitId
            },
            timecard: {
                shift_id: this.shiftId,
                clock_in: this.clockInTime,
                clock_out: this.clockOutTime,
                total_shift_seconds: totalShiftSeconds,
                breaks: this.breaks,
                net_payable_hours: parseFloat(netPayableHours.toFixed(2))
            },
            incident_history: this.incidentLogs,
            evidence_manifest: this.evidencePackage,
            hazards_and_exposures: this.exposuresAndHazards
        };

        // Seal the entire payload with a master shift hash
        const payloadHash = crypto.createHash('sha256')
            .update(JSON.stringify(payload))
            .digest('hex');

        payload.master_shift_hash = payloadHash;
        return payload;
    }
}

module.exports = BaseFirstResponderModule;
