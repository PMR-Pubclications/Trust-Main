// modules/fire/StructuralFirefighterModule.js
const BaseFirstResponderModule = require('../firstResponder/BaseFirstResponderModule');

class StructuralFirefighterModule extends BaseFirstResponderModule {
    /**
     * @param {string} badgeId - Firefighter badge or employee ID
     * @param {string} agencyId - e.g., "VANCOUVER_FIRE_RESCUE", "FDNY", "SEATTLE_FIRE"
     * @param {string} unitId - e.g., "ENGINE-1", "TRUCK-4", "SQUAD-2"
     * @param {string} ridingPosition - e.g., "NOZZLE", "HYDRANT", "CAPTAIN", "DRIVER", "IRIC"
     */
    constructor(badgeId, agencyId, unitId, ridingPosition = "NOZZLE") {
        super(badgeId, agencyId, unitId);
        this.ridingPosition = ridingPosition;

        // SCBA Air Management
        this.scbaLogs = [];
        this.currentScbaBottlePsi = 4500; // Standard 4500 PSI or 5500 PSI bottle

        // Fireground Operations
        this.atmosphericReadings = [];
        this.tacticalSearchLogs = [];
        this.suppressionMode = "OFFENSIVE"; // 'OFFENSIVE', 'DEFENSIVE', 'TRANSITIONAL'
    }

    // ==========================================
    // STRUCTURAL FIRE SPECIFIC METHODS
    // ==========================================

    /**
     * Track SCBA air consumption & cylinder changes during interior attack
     */
    logScbaBottleEntry(startPsi, bottleCapacityPsi = 4500) {
        this.currentScbaBottlePsi = startPsi;
        const entryRecord = {
            bottle_id: `BOTTLE_${Date.now()}`,
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "UNKNOWN",
            start_psi: startPsi,
            end_psi: null,
            duration_minutes: null,
            capacity_psi: bottleCapacityPsi
        };

        this.scbaLogs.push(entryRecord);
        if (this.activeIncident) {
            this.logActivity(`SCBA air tank on. Entry pressure: ${startPsi} PSI.`);
        }
        return entryRecord;
    }

    logScbaBottleExit(endPsi) {
        if (this.scbaLogs.length === 0 || this.scbaLogs[this.scbaLogs.length - 1].end_psi !== null) {
            throw new Error("No active SCBA entry bottle session to exit.");
        }

        const activeBottle = this.scbaLogs[this.scbaLogs.length - 1];
        const exitTime = new Date();
        const entryTime = new Date(activeBottle.timestamp);
        
        activeBottle.end_psi = endPsi;
        activeBottle.duration_minutes = parseFloat(((exitTime - entryTime) / 60000).toFixed(2));
        
        const psiConsumed = activeBottle.start_psi - endPsi;

        if (this.activeIncident) {
            this.logActivity(`SCBA air tank off. Exit pressure: ${endPsi} PSI (${psiConsumed} PSI consumed in ${activeBottle.duration_minutes} min).`);
        }

        // Low air alarm triggered (< 25-33% capacity remaining)
        if (endPsi < (activeBottle.capacity_psi * 0.25)) {
            this.recordHazardOrExposure('PHYSICAL_IMPACT', 'MEDIUM', `VIBRALERT / Low Air Alarm active on exit (${endPsi} PSI remaining).`);
        }

        return activeBottle;
    }

    /**
     * Record 4-gas monitor atmospheric gas levels (Hazmat/CO/Flashover risk)
     */
    logAtmosphericReading(coPpm, h2sPpm, o2Percentage, lelPercentage) {
        const reading = {
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "ATMOSPHERIC_CHECK",
            co_ppm: coPpm,
            h2s_ppm: h2sPpm,
            o2_percent: o2Percentage,
            lel_percent: lelPercentage
        };

        this.atmosphericReadings.push(reading);

        // Auto-detect hazardous atmospheric conditions
        if (coPpm > 35 || o2Percentage < 19.5 || lelPercentage > 10) {
            this.recordHazardOrExposure('CHEMICAL', 'HIGH', `IDLH or Toxic Atmosphere detected: CO ${coPpm} PPM, O2 ${o2Percentage}%, LEL ${lelPercentage}%`);
        }

        return reading;
    }

    /**
     * Log primary/secondary search completion and BENBC (Breadcrumbs)
     */
    logTacticalSearch(floorLevel, searchType = "PRIMARY", result = "CLEAR") {
        const record = {
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "FIRE_SEARCH",
            floor_level: floorLevel,
            search_type: searchType, // 'PRIMARY', 'SECONDARY'
            result: result           // 'CLEAR', 'VICTIM_LOCATED', 'HAZARD_BLOCKED'
        };

        this.tacticalSearchLogs.push(record);
        if (this.activeIncident) {
            this.logActivity(`${searchType} search on ${floorLevel}: ${result}`);
        }
        return record;
    }

    /**
     * Switch tactical posture (e.g., Command orders evacuation to Defensive)
     */
    setTacticalSuppressionMode(mode) {
        this.suppressionMode = mode; // 'OFFENSIVE', 'DEFENSIVE', 'TRANSITIONAL'
        if (this.activeIncident) {
            this.logActivity(`Tactical posture changed to: ${mode}`);
        }
    }

    /**
     * Override clockOut to aggregate Structural Firefighter payload
     */
    clockOut() {
        const basePayload = super.clockOut();
        
        const totalAirTimeMinutes = this.scbaLogs.reduce((acc, log) => acc + (log.duration_minutes || 0), 0);

        basePayload.module = "STRUCTURAL_FIREFIGHTER";
        basePayload.fire_specifics = {
            riding_position: this.ridingPosition,
            total_scba_bottles_used: this.scbaLogs.length,
            total_air_time_minutes: parseFloat(totalAirTimeMinutes.toFixed(2)),
            scba_session_logs: this.scbaLogs,
            atmospheric_readings: this.atmosphericReadings,
            tactical_search_history: this.tacticalSearchLogs,
            final_suppression_mode: this.suppressionMode
        };

        // Re-seal master shift hash with fire metrics included
        const crypto = require('crypto');
        basePayload.master_shift_hash = crypto.createHash('sha256')
            .update(JSON.stringify(basePayload))
            .digest('hex');

        return basePayload;
    }
}

module.exports = StructuralFirefighterModule;
