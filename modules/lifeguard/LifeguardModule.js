// modules/lifeguard/LifeguardModule.js
const BaseFirstResponderModule = require('../firstResponder/BaseFirstResponderModule');

class LifeguardModule extends BaseFirstResponderModule {
    /**
     * @param {string} badgeId - Lifeguard badge or employee ID
     * @param {string} agencyId - e.g., "LA_COUNTY_LIFEGUARD", "SAN_DIEGO_FIRE_RESCUE_LIFESAVING"
     * @param {string} unitId - e.g., "RWC-1" (Rescue Water Craft), "CUTTER-3", "TOWER-14"
     * @param {string} towerPostId - Specific station or beach zone tower identifier
     */
    constructor(badgeId, agencyId, unitId, towerPostId = "MAIN_TOWER") {
        super(badgeId, agencyId, unitId);
        this.towerPostId = towerPostId;

        // Domain Metrics
        this.waterRescues = [];
        this.preventativeActions = 0;
        this.spinalImmobilizations = [];
        this.oceanConditions = {
            surf_height_feet: 0,
            rip_current_risk: "LOW", // 'LOW', 'MODERATE', 'HIGH', 'EXTREME'
            water_temp_f: 0
        };
    }

    // ==========================================
    // LIFEGUARD SPECIFIC METHODS
    // ==========================================
    
    /**
     * Set environmental water safety parameters for the tower/zone
     */
    updateOceanConditions(surfHeight, ripRisk, waterTempF) {
        this.oceanConditions = {
            surf_height_feet: surfHeight,
            rip_current_risk: ripRisk,
            water_temp_f: waterTempF,
            last_updated: new Date().toISOString()
        };

        if (this.activeIncident) {
            this.logActivity(`Ocean conditions updated: ${surfHeight}ft surf, ${ripRisk} rip risk.`);
        }
    }

    /**
     * Log an active open-water or surf rescue
     */
    logWaterRescue(victimCategory, rescueTool, distanceOffshoreYards) {
        const rescueRecord = {
            rescue_id: `RESCUE_${Date.now()}`,
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "PREVENTATIVE_SWIM_RESCUE",
            victim_category: victimCategory, // 'ADULT', 'JUVENILE', 'DISTRESSED_SWIMMER', 'UNCONSCIOUS'
            rescue_tool: rescueTool,           // 'RESCUE_CAN', 'RESCUE_BOARD', 'RWC_JETSKI', 'SWIM_FINS'
            distance_offshore_yards: distanceOffshoreYards
        };

        this.waterRescues.push(rescueRecord);
        
        // Auto-log event inside current incident if active
        if (this.activeIncident) {
            this.logActivity(`Water rescue executed. Tool: ${rescueTool}, Distance: ${distanceOffshoreYards} yds.`);
        }

        return rescueRecord;
    }

    /**
     * Track swimmer interventions before they turn into full rescues
     */
    logPreventativeActions(count = 1, actionType = "RIP_CURRENT_WARNING") {
        this.preventativeActions += count;
        if (this.activeIncident) {
            this.logActivity(`Logged ${count} preventative action(s): ${actionType}`);
        }
    }

    /**
     * High-risk coastal cliff or surf zone spinal injury extraction
     */
    logSpinalImmobilization(victimCondition, extractionMethod) {
        const record = {
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "UNSCHEDULED_EMS",
            condition: victimCondition,
            method: extractionMethod // 'BACKBOARD_IN_SURF', 'HIGH_ANGLE_ROPE_LIFT', 'RWC_SLED'
        };

        this.spinalImmobilizations.push(record);
        
        // Log biological/physical hazard exposure risk to base module
        this.recordHazardOrExposure('PHYSICAL_IMPACT', 'HIGH', `Spinal extraction executed in surf: ${extractionMethod}`);
        
        return record;
    }

    /**
     * Override clockOut to aggregate Lifeguard payload
     */
    clockOut() {
        const basePayload = super.clockOut();
        
        basePayload.module = "OCEAN_LIFEGUARD";
        basePayload.lifeguard_specifics = {
            tower_post_id: this.towerPostId,
            total_water_rescues: this.waterRescues.length,
            water_rescue_records: this.waterRescues,
            total_preventative_actions: this.preventativeActions,
            spinal_immobilizations: this.spinalImmobilizations,
            final_ocean_conditions: this.oceanConditions
        };

        // Re-seal master shift hash with lifeguard metrics included
        const crypto = require('crypto');
        basePayload.master_shift_hash = crypto.createHash('sha256')
            .update(JSON.stringify(basePayload))
            .digest('hex');

        return basePayload;
    }
}

module.exports = LifeguardModule;
