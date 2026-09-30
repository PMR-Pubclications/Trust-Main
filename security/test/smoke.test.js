// security/test/smoke.test.js
//
// Lightweight smoke test (no external test framework dependency) that:
//   1. Boots the security service on an ephemeral port.
//   2. Verifies /health responds.
//   3. Verifies /status reports the module boundaries (voice mounted,
//      nfc/face/gait/auth explicitly marked as not-mounted stubs).
//   4. Exercises the voice telemetry endpoint end-to-end (arrival + a
//      duplicate-arrival conflict) to confirm the reorganized
//      voice/VoiceAndRadioCodeTelemetry.js module still works after the
//      move from asset/js/ferensics/.
//
// Run with: node security/test/smoke.test.js  (or `npm test` from security/)
'use strict';

const http = require('http');
const assert = require('assert');
const app = require('../server.js');

function request(port, method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const req = http.request(
      {
        host: '127.0.0.1',
        port,
        path: urlPath,
        method,
        headers: payload
          ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
          : {}
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          let parsed = null;
          try {
            parsed = data ? JSON.parse(data) : null;
          } catch (e) {
            parsed = data;
          }
          resolve({ status: res.statusCode, body: parsed });
        });
      }
    );
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

async function main() {
  const server = app.listen(0);
  const port = server.address().port;

  try {
    const health = await request(port, 'GET', '/health');
    assert.strictEqual(health.status, 200, 'expected /health to return 200');
    assert.strictEqual(health.body.ok, true, 'expected /health body.ok === true');

    const status = await request(port, 'GET', '/status');
    assert.strictEqual(status.status, 200, 'expected /status to return 200');
    assert.strictEqual(status.body.modules.voice.mounted, true, 'voice module should be mounted');
    assert.strictEqual(status.body.modules.nfc.mounted, false, 'nfc is a browser-only stub, should not be mounted');
    assert.strictEqual(status.body.modules.face.mounted, false, 'face recognition is not implemented, should not be mounted');
    assert.strictEqual(status.body.modules.gait.mounted, false, 'gait recognition is not implemented, should not be mounted');

    const unitId = `smoke-test-unit-${Date.now()}`;
    const arrival = await request(port, 'POST', '/api/v1/trust/telemetry', {
      unitId,
      voicePrintToken: 'any-value-because-verifyVoiceToken-is-a-stub',
      radioCode: '10-23',
      coordinates: { lat: 45.0, lng: -122.0 }
    });
    assert.strictEqual(arrival.status, 200, 'expected 10-23 arrival to succeed');
    assert.strictEqual(arrival.body.status, 'SUCCESS');

    const duplicateArrival = await request(port, 'POST', '/api/v1/trust/telemetry', {
      unitId,
      voicePrintToken: 'any-value',
      radioCode: '10-23'
    });
    assert.strictEqual(duplicateArrival.status, 400, 'expected duplicate 10-23 arrival to conflict');

    const departure = await request(port, 'POST', '/api/v1/trust/telemetry', {
      unitId,
      voicePrintToken: 'any-value',
      radioCode: '10-8'
    });
    assert.strictEqual(departure.status, 200, 'expected 10-8 departure to succeed');
    assert.strictEqual(typeof departure.body.evidenceHash, 'string');

    console.log('OK: security smoke tests passed');
  } finally {
    server.close();
  }
}

main().catch((err) => {
  console.error('FAILED:', err);
  process.exitCode = 1;
});
