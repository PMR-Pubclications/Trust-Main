// index.js
const StructuralFirefighterModule = require('./modules/fire/StructuralFirefighterModule');
const TrustOfflineBuffer = require('./lib/TrustOfflineBuffer');

// 1. Initialize Buffer with Trust-Main API endpoint
const buffer = new TrustOfflineBuffer(
    './data/trust_shell_queue.db', 
    'https://trust-main.internal/api/v1/telemetry/ingest'
);

// 2. Start background network monitor loop (checks every 10 seconds)
buffer.startAutoSync(10000);

// 3. Create a shift and clock out while offline
const ff = new StructuralFirefighterModule("FF-902", "VANCOUVER_FIRE_RESCUE", "ENGINE-1", "NOZZLE");
ff.clockIn({ lat: 45.6318, lng: -122.6716 });
ff.startIncident("CAD-2026-9901", "STRUCTURE_FIRE_COMMERCIAL", { lat: 45.6350, lng: -122.6750 });
ff.logScbaBottleEntry(4500);
ff.logScbaBottleExit(1200);
ff.clearIncident();

// 4. Generate shift payload
const payload = ff.clockOut();

// 5. Safely buffer payload locally in SQLite
const enqueueRef = buffer.enqueue(payload);
console.log(`[Trust-Shell] Shift payload buffered locally. Queue ID: ${enqueueRef.queueId}`);

// Check local stats
console.log('[Trust-Shell] Queue Status:', buffer.getQueueStats());
