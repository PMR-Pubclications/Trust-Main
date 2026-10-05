// modules/dot/DotIncidentModule.js
const BaseFirstResponderModule = require('../firstResponder/BaseFirstResponderModule');

class DotIncidentModule extends BaseFirstResponderModule {
    constructor(badgeId, agencyId, unitId) {
        super(badgeId, agencyId, unitId);
        this.laneClosures = [];
        this.debrisClearedInTons = 0;
    }

    logLaneClosure(laneNumber, blockType) {
        const record = {
            timestamp: new Date().toISOString(),
            cad_number: this.activeIncident ? this.activeIncident.cad_number : "UNKNOWN",
            lane: laneNumber,
            block_type: blockType // 'ATTENUATOR_TRUCK', 'CONES', 'ARROW_BOARD'
        };
        this.laneClosures.push(record);
        this.logActivity(`Lane ${laneNumber} closed using ${blockType}`);
    }

    clockOut() {
        const basePayload = super.clockOut();
        basePayload.module = "DOT_INCIDENT_RESPONSE";
        basePayload.dot_specifics = {
            lane_closures_executed: this.laneClosures,
            debris_cleared_tons: this.debrisClearedInTons
        };
        return basePayload;
    }
}

module.exports = DotIncidentModule;
