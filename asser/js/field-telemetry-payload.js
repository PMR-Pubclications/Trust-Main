/**
 * ----------------------------------------------------------------------------
 * Module: Field Telemetry & Sensor Integration
 * Author: Anatolie Anatoliciva
 * Description: Merges camera spatial measurements and thermal readings into 
 *              the active forensic report package.
 * ----------------------------------------------------------------------------
 */
const fieldTelemetryIntegration = {

    // Compile camera measurement and thermal data into a unified telemetry object
    async compileTelemetryPackage(spatialData, thermalData) {
        const timestamp = new Date().toISOString();
        
        const telemetryRecord = {
            telemetry_id: `TEL_${Date.now()}`,
            timestamp: timestamp,
            station_context: {
                operator: document.getElementById('lbl-operator') ? document.getElementById('lbl-operator').innerText : 'Anatolie Anatoliciva',
                location: "Vancouver, Washington"
            },
            spatial_measurement: spatialData ? {
                raw_meters: spatialData.raw_meters,
                formatted_distance: spatialData.formatted_output,
                unit: spatialData.unit_type
            } : { status: "NO_SPATIAL_DATA_CAPTURED" },
            environmental_thermal: thermalData ? {
                value: thermalData.converted_value,
                unit: thermalData.unit,
                formatted: thermalData.formatted,
                sensor_source: "Mobile Hardware / Battery Thermal Interface"
            } : { status: "THERMAL_SENSOR_UNAVAILABLE" }
        };

        console.log('[TELEMETRY] Successfully compiled field sensor payload:', telemetryRecord);
        return telemetryRecord;
    },

    // Execute capture, package, and commit to cloud/report buffer
    async captureAndAppendToReport(appInstance) {
        // 1. Gather active camera measurement (assuming spatialMeasurementTool has run)
        const spatialResult = typeof spatialMeasurementTool !== 'undefined' ? spatialMeasurementTool.calculateDistance() : null;

        // 2. Gather active hardware thermal reading
        const thermalResult = typeof deviceTemperatureTool !== 'undefined' ? await deviceTemperatureTool.fetchDeviceTemperature() : null;

        // 3. Compile the payload
        const finalPayload = await this.compileTelemetryPackage(spatialResult, thermalResult);

        // 4. Append to active trail or push to repository via your app instance
        if (appInstance && typeof appInstance.spatialTrail !== 'undefined') {
            appInstance.spatialTrail.push(finalPayload);
            
            // If connected to GitHub, commit the updated package
            const todayStr = new Date().toISOString().split('T')[0];
            const filePath = `forensic_data/telemetry_log_${todayStr}.json`;
            
            if (typeof appInstance.commitFileToGitHub === 'function') {
                await appInstance.commitFileToGitHub(filePath, appInstance.spatialTrail, `Append field telemetry & sensor data`);
                alert('Camera measurement and thermal data successfully appended and committed to repository.');
            }
        }

        return finalPayload;
    }
};
