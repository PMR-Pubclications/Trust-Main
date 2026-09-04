/**
 * ----------------------------------------------------------------------------
 * Module: Camera Spatial Measurement (WebXR / Hit-Test Engine)
 * Author: Anatolie Anatoliciva
 * Description: Calculates physical distance between two targeted points via camera.
 * ----------------------------------------------------------------------------
 */
const spatialMeasurementTool = {
    firstPoint: null,
    secondPoint: null,
    measurementUnit: 'metric', // 'metric' (cm) or 'imperial' (inches)

    // Check if WebXR immersive-ar with hit-test is supported on the field device
    async initializeARMeasurementSession() {
        if (!navigator.xr || !await navigator.xr.isSessionSupported('immersive-ar')) {
            console.warn('[AR] WebXR immersive-ar not supported on this terminal. Using fallback sensor mode.');
            return false;
        }
        return true;
    },

    // Capture point when operator taps/clicks a surface in the camera view
    recordSpatialPoint(hitTestResultMatrix, pointIdentifier) {
        const position = {
            x: hitTestResultMatrix[12],
            y: hitTestResultMatrix[13],
            z: hitTestResultMatrix[14]
        };

        if (pointIdentifier === 'POINT_A') {
            this.firstPoint = position;
            console.log('[MEASURE] Origin Point A locked:', this.firstPoint);
        } else if (pointIdentifier === 'POINT_B') {
            this.secondPoint = position;
            console.log('[MEASURE] Target Point B locked:', this.secondPoint);
            return this.calculateDistance();
        }
        return null;
    },

    // Calculate 3D Euclidean distance between Point A and Point B
    calculateDistance() {
        if (!this.firstPoint || !this.secondPoint) {
            alert('Both Point A and Point B must be recorded.');
            return null;
        }

        const dx = this.secondPoint.x - this.firstPoint.x;
        const dy = this.secondPoint.y - this.firstPoint.y;
        const dz = this.secondPoint.z - this.firstPoint.z;

        // Distance in meters
        const distanceMeters = Math.sqrt(dx * dx + dy * dy + dz * dz);

        let formattedResult = '';
        if (this.measurementUnit === 'imperial') {
            const totalInches = distanceMeters * 39.3701;
            const feet = Math.floor(totalInches / 12);
            const inches = (totalInches % 12).toFixed(2);
            formattedResult = feet > 0 ? `${feet} ft ${inches} in` : `${inches} inches`;
        } else {
            const centimeters = (distanceMeters * 100).toFixed(1);
            formattedResult = `${centimeters} cm (${distanceMeters.toFixed(3)} m)`;
        }

        console.log(`[MEASUREMENT RESULT] Distance: ${formattedResult}`);
        return {
            raw_meters: distanceMeters,
            formatted_output: formattedResult,
            unit_type: this.measurementUnit
        };
    },

    setUnit(unit) {
        this.measurementUnit = unit; // 'metric' or 'imperial'
    }
};
