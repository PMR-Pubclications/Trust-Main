# /security — Trust Security & Biometric Integration Layer

This directory consolidates every security-, authentication-, and
biometric-related source file that previously lived scattered under
`asset/js`, `asset/java`, and `asset/cpp`. It also adds everything needed
to run the server-side pieces as a **standalone service on a Linux server**,
independent of the rest of the `Trust` repository.

> **Scope honesty:** this repository does not contain a working face,
> gait, or voice *recognition* algorithm. What exists are: a shared camera
> capture interface (used to feed frames into a future face/gait
> pipeline), a voice-token telemetry endpoint whose token verification is
> an explicit stub (`verifyVoiceToken()` always returns `true`), a
> browser-only Web NFC snippet, and a set of Java authorization/passkey
> utilities. Nothing here should be presented as production-ready
> biometric recognition.

## Directory layout

```
security/
├── nfc/                      Browser-only Web NFC authentication snippet
│   ├── NFC_Tap-to-Authenticate.js
│   └── README.md             Explains why it can't run on a headless server
├── voice/                    Voice-token gated telemetry + voice biometric stub
│   ├── VoiceAndRadioCodeTelemetry.js   (Express router, runs in server.js)
│   └── VoiceBiometricGatekeeper.java   (Java voice-hash comparison stub)
├── auth/                     Authentication / authorization / passkey utilities (Java)
│   ├── SecurityFilter.java
│   ├── LoginServlet.java
│   ├── SecurityCoreUtils.java
│   ├── SecureTokenGenerator.java
│   ├── SecureTrustAndForensicGateway.java   (passkey signature verification + evidence routing)
│   ├── PoliceEvidenceFirewall.java
│   ├── SecureAssetFirewall.java
│   └── android/
│       └── KeyGenParameterSpec.java  (Android biometric-gated key generation snippet)
├── native/
│   └── camera/                Cross-platform camera capture abstraction
│       ├── include/            CameraInterface.h, CameraFactory.h, Platform.h
│       ├── android/             Android Camera2 NDK backend
│       ├── ios/                 iOS AVFoundation backend
│       ├── linux/               Linux V4L2 backend
│       └── CMakeLists.txt        Builds whichever backend matches the host/target
├── docs/
│   └── MIGRATION.md           File-by-file move/rename mapping
├── test/
│   └── smoke.test.js          Node smoke test for the standalone service
├── server.js                  Standalone Express entry point (Linux server)
├── package.json / package-lock.json
├── Dockerfile
├── docker-compose.yml
├── deploy.sh
├── trust-security.service     Optional systemd unit (no-Docker alternative)
├── .env.example
└── .gitignore
```

## What actually runs as "the security service"

`security/server.js` is the only piece that runs as a long-lived Linux
process today. It is a small Express app that:

* exposes `GET /health` for container/orchestrator health checks,
* exposes `GET /status`, which reports which modules are mounted vs. which
  are stubs/not-applicable on a server (`face`, `gait`, `nfc` are reported
  `mounted: false`),
* mounts `voice/VoiceAndRadioCodeTelemetry.js` at `/api/v1/trust`
  (behind a lightweight in-memory rate limiter — see
  `SECURITY_RATE_LIMIT_WINDOW_MS`/`SECURITY_RATE_LIMIT_MAX_REQUESTS`),
  which implements the `10-23`/`10-8` radio-code arrival/departure
  workflow gated behind `verifyVoiceToken()` — **a stub that always
  returns true**.

The `nfc/`, `auth/`, and `native/camera/` code is **not** loaded by
`server.js`:

* `nfc/NFC_Tap-to-Authenticate.js` is a browser-only fragment (Web NFC
  API), meant to be embedded in a front-end page — see
  `security/nfc/README.md`.
* `auth/*.java` are Java servlet-filter/authorization/passkey utilities
  that target a Jakarta/Java EE servlet container (e.g. Tomcat), not
  Node.js. They are preserved here for organization and review, but are
  not wired into any build in this repository (none existed before the
  move either — see `docs/MIGRATION.md`).
* `native/camera/` is a C++/Objective-C++ camera capture abstraction
  built with CMake, independent of the Node service (see below).

## Runtime dependencies

### Voice/NFC/status service (Node.js)
* Node.js >= 18
* npm dependencies: `express` (see `package.json`)

### Native camera module (optional, C++)
* CMake >= 3.18
* A C++17 compiler (g++/clang++)
* Linux target: Linux kernel headers providing `<linux/videodev2.h>`
  (V4L2) — present on virtually all Linux distributions via `libc6-dev`/
  kernel headers.
* Android target: Android NDK + `camera2ndk`/`mediandk` (cross-compiled
  via Gradle/NDK, not on the Linux server itself).
* iOS target: Xcode + AVFoundation (macOS only, not on the Linux server).

### Auth utilities (optional, Java)
* JDK 17+
* A servlet container providing `javax.servlet`/`jakarta.servlet` APIs
  (e.g. Apache Tomcat) and `org.mindrot.jbcrypt` for `LoginServlet.java`.
  These are **not bundled**; this repository never built them before the
  reorganization either.

## Configuration

Copy `security/.env.example` to `security/.env` and fill in real values.
**Never commit `security/.env`.** See `.env.example` for the full list of
placeholders (`SECURITY_PORT`, `SECURITY_ADMIN_KEY`, `SECURITY_DATA_DIR`).

## Local development

```bash
cd security
npm install
cp .env.example .env     # edit values as needed
npm start                 # runs server.js on http://localhost:3100
npm test                  # runs the smoke test suite
```

## Linux deployment

### Option A — Docker (recommended)

```bash
cd /path/to/Trust-Main
cp security/.env.example security/.env   # edit real values
./security/deploy.sh          # build + start
./security/deploy.sh logs     # tail logs
./security/deploy.sh down     # stop
```

This uses `security/docker-compose.yml`, which builds `security/Dockerfile`
with the **repository root** as the build context (so only the
`security/` files are copied into the image), runs the container as a
non-root `security` user, restarts `unless-stopped`, and exposes a Docker
`HEALTHCHECK` against `/health`. Application data is kept in the named
volume `trust-security-data` mounted at `/app/data` — no biometric data is
written there by anything in this repository today.

### Option B — systemd (no Docker)

See the header comment in `security/trust-security.service` for full
install steps: create a dedicated `trust-security` system user, install
files under `/opt/trust-security`, place `.env` there with `chmod 600`,
then `systemctl enable --now trust-security`. The unit applies standard
systemd sandboxing (`ProtectSystem=strict`, `NoNewPrivileges=true`,
`PrivateTmp=true`, etc.) and restarts on failure.

### Logging & persistence guidance

* The service logs to stdout/stderr only (`console.log`/`console.error`);
  under Docker use `docker logs` / `docker compose logs`, under systemd
  use `journalctl -u trust-security`.
* **Never log biometric payloads.** The voice telemetry stub only logs a
  SHA-256 *hash* of the session object (`generateEvidenceHash`), never
  the raw `voicePrintToken`. Keep it that way if you extend this code.
* Persistent storage (`/app/data` in Docker, `/var/lib/trust-security`
  under systemd) is reserved for non-biometric audit/ledger data only.

## Hardware / device limitations

* NFC scanning requires a physical NFC reader and a supporting mobile
  browser — it cannot function inside a headless server container.
* The native camera backends require an actual camera device
  (`/dev/videoN` on Linux, Camera2 on Android, AVFoundation on iOS); on a
  headless server without a camera, `LinuxCameraBackend::findCameras()`
  will simply return an empty list, which is expected and non-fatal.
* Face and gait *recognition* algorithms are not implemented anywhere in
  this repository; only the shared camera capture interface exists.

## Security & privacy assumptions

* `.env`, certificates, keys, and any biometric artifacts are excluded via
  `security/.gitignore` and must never be committed.
* The voice-token check is a stub; do not treat it as an authentication
  control in any real deployment until real verification is implemented.
* Docker images are built without any secrets baked in; all configuration
  is supplied at runtime via `security/.env` / `env_file`.
* The Docker container and the systemd unit both run as a dedicated
  non-root user.

## Migration note

See [`docs/MIGRATION.md`](docs/MIGRATION.md) for the full file-by-file
mapping of what moved from `asset/js`, `asset/java`, and `asset/cpp` into
`/security`, including the filename/typo corrections that were made and
why they are safe (nothing else in the repository referenced the old
names).
