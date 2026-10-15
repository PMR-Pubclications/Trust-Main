// test_tamper.js
const TrustOfflineBuffer = require('./lib/TrustOfflineBuffer');

const buffer = new TrustOfflineBuffer('./trust_shell_queue.db', 'https://trust-main.internal/api/v1/telemetry/ingest');

// 1. Enqueue valid payload
const payload = { master_shift_hash: "a1b2c3d4", badge_id: "FF-902", data: "Original telemetry" };
const { queueId } = buffer.enqueue(payload);

// 2. Simulate raw SQLite database modification (Disk Tampering)
buffer.db.prepare(`UPDATE payload_queue SET payload_json = ? WHERE queue_id = ?`)
    .run(JSON.stringify({ master_shift_hash: "a1b2c3d4", badge_id: "FF-902", data: "ALTERED TELEMETRY" }), queueId);

// 3. Attempt verification
const record = buffer.db.prepare(`SELECT * FROM payload_queue WHERE queue_id = ?`).get(queueId);
const isIntegrityIntact = buffer.verifyRecordIntegrity(record);

console.log(`Is Payload Valid? ${isIntegrityIntact}`); // Output: false

// 4. Check status in DB
const updatedRecord = buffer.db.prepare(`SELECT status, error_log FROM payload_queue WHERE queue_id = ?`).get(queueId);
console.log(`Updated Status: ${updatedRecord.status}`); // Output: TAMPERED
console.log(`Error Log: ${updatedRecord.error_log}`);
