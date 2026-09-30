// security/server.js
//
// Standalone entry point for the Trust "security" service on a headless
// Linux server. This process intentionally only wires up the parts of the
// repository's security/biometric code that are pure server-side Node.js:
//
//   - voice/VoiceAndRadioCodeTelemetry.js  (Express router, voice-token
//     gated radio-code telemetry ingestion)
//
// It deliberately does NOT attempt to run:
//   - nfc/NFC_Tap-to-Authenticate.js   -> requires a browser Web NFC API
//     (window, NDEFReader) and a physical NFC reader; it is a front-end
//     snippet meant to be embedded in a browser page, not server code.
//   - native/camera/*                  -> C++/Obj-C++ camera capture
//     backends for Android/iOS/Linux, built separately via CMake (see
//     native/camera/CMakeLists.txt). They are not Node modules.
//   - auth/*.java                      -> servlet/authorization utilities
//     meant for a Java/Jakarta EE application server, built and deployed
//     independently (see README.md).
//
// verifyVoiceToken() inside VoiceAndRadioCodeTelemetry.js is a documented
// stub that always returns true; this service does NOT implement working
// voice biometric recognition.
'use strict';

const express = require('express');
const path = require('path');

const voiceTelemetryRouter = require(path.join(__dirname, 'voice', 'VoiceAndRadioCodeTelemetry.js'));

const app = express();
const PORT = Number(process.env.SECURITY_PORT || 3100);

app.use(express.json({ limit: '100kb' }));

app.get('/health', (req, res) => {
  res.json({ ok: true, service: 'trust-security', timestamp: new Date().toISOString() });
});

// Describes which security modules are live server endpoints vs. stubs
// that live elsewhere (browser/mobile/native) so operators don't assume
// face/gait/NFC recognition is running here.
app.get('/status', (req, res) => {
  res.json({
    service: 'trust-security',
    modules: {
      voice: { mounted: true, path: '/api/v1/trust', stub: true, note: 'verifyVoiceToken() always returns true; no real voice biometric matching is implemented.' },
      nfc: { mounted: false, reason: 'browser-only Web NFC snippet, see security/nfc/README.md' },
      auth: { mounted: false, reason: 'Java servlet/authorization utilities, deployed separately, see security/auth' },
      face: { mounted: false, reason: 'no face recognition implementation in this repository; only shared camera capture interfaces exist under security/native/camera' },
      gait: { mounted: false, reason: 'no gait recognition implementation in this repository; only shared camera capture interfaces exist under security/native/camera' }
    }
  });
});

// Minimal fixed-window rate limiter for the voice-token telemetry
// endpoint. This route performs authorization (verifyVoiceToken) and
// must not be left unbounded, or it becomes a brute-force / DoS vector.
// Kept dependency-free on purpose; swap for a shared store (e.g. Redis)
// if this service is ever scaled horizontally behind a load balancer.
const RATE_LIMIT_WINDOW_MS = Number(process.env.SECURITY_RATE_LIMIT_WINDOW_MS || 60_000);
const RATE_LIMIT_MAX_REQUESTS = Number(process.env.SECURITY_RATE_LIMIT_MAX_REQUESTS || 30);
const rateLimitBuckets = new Map();

function telemetryRateLimiter(req, res, next) {
  const key = req.ip || req.socket.remoteAddress || 'unknown';
  const now = Date.now();
  const bucket = rateLimitBuckets.get(key);

  if (!bucket || now - bucket.windowStart >= RATE_LIMIT_WINDOW_MS) {
    rateLimitBuckets.set(key, { windowStart: now, count: 1 });
    return next();
  }

  if (bucket.count >= RATE_LIMIT_MAX_REQUESTS) {
    res.set('Retry-After', String(Math.ceil((RATE_LIMIT_WINDOW_MS - (now - bucket.windowStart)) / 1000)));
    return res.status(429).json({ error: 'Too many requests. Please slow down.' });
  }

  bucket.count += 1;
  return next();
}

app.use('/api/v1/trust', telemetryRateLimiter, voiceTelemetryRouter);

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`[trust-security] listening on http://0.0.0.0:${PORT}`);
  });
}

module.exports = app;
