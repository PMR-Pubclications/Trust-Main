const path = require('path');

let nativeHardware = null;

try {
  // Load the compiled C++ binary from node-gyp build directory
  nativeHardware = require(path.join(__dirname, '../../build/Release/hardware_bridge.node'));
  console.log('[Hardware Bridge] Native C++ module loaded successfully.');
} catch (err) {
  console.error('[Hardware Bridge] Failed to load native binary:', err.message);
}

/**
 * Interface to interact with native hardware registers
 */
module.exports = {
  isAvailable: () => nativeHardware !== null,

  /**
   * Retrieves current temperature from low-level thermal sensor
   * @returns {number|null} Temperature in Celsius
   */
  getTemperature: () => {
    if (!nativeHardware) return null;
    return nativeHardware.getTemperature();
  },

  /**
   * Reads raw thermal buffer from native memory
   * @returns {Float32Array|null}
   */
  captureThermalFrame: () => {
    if (!nativeHardware) return null;
    const rawBuffer = nativeHardware.captureThermalFrame();
    return new Float32Array(rawBuffer);
  }
};
