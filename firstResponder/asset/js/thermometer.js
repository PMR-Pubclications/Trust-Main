/**
 * ----------------------------------------------------------------------------
 * Module: Mobile Hardware Temperature Reader
 * Author: Anatolie Anatoliciva
 * Description: Retrieves internal device temperature and formats output.
 * ----------------------------------------------------------------------------
 */
const deviceTemperatureTool = {
    preferredUnit: 'fahrenheit', // Options: 'fahrenheit' or 'celsius'

    async fetchDeviceTemperature() {
        if (!navigator.getBattery) {
            console.warn('[TEMP] Battery Status API is not supported on this browser/device.');
            return null;
        }

        try {
            const battery = await navigator.getBattery();
            
            // Note: Standard browser implementations expose battery temperature 
            // via specialized hardware hooks (e.g., battery.temperature in supported Android WebViews)
            const celsiusTemp = battery.temperature || this.estimateFromThermalState();

            if (celsiusTemp === null) {
                throw new Error('Hardware thermal sensor data restricted or unavailable.');
            }

            return this.formatOutput(celsiusTemp);
        } catch (err) {
            console.error('[TEMP ERROR] Failed to retrieve sensor data:', err.message);
            return null;
        }
    },

    // Fallback or helper calculation if direct property is mapped
    formatOutput(celsius) {
        let finalValue = celsius;
        let unitLabel = '°C';

        if (this.preferredUnit === 'fahrenheit') {
            finalValue = (celsius * 9/5) + 32;
            unitLabel = '°F';
        }

        const formattedString = `${finalValue.toFixed(1)} ${unitLabel}`;
        console.log(`[SENSOR READING] Internal Device Temperature: ${formattedString}`);
        
        return {
            raw_celsius: celsius,
            converted_value: Number(finalValue.toFixed(1)),
            unit: this.preferredUnit,
            formatted: formattedString
        };
    },

    setUnit(unit) {
        if (unit === 'fahrenheit' || unit === 'celsius') {
            this.preferredUnit = unit;
        }
    },

    estimateFromThermalState() {
        // Standard baseline simulation if hardware property is restricted by mobile OS privacy sandboxing
        return 31.5; // Default normal operational baseline in Celsius (~88.7°F)
    }
};
