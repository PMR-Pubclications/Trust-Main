# Migration note: consolidation into `/security`

This document lists every file moved during the `/security` reorganization,
why each was chosen, and any filename corrections applied. Nothing in this
list changed program behavior — only file paths, and in the cases noted
below, filenames that did not match a file's actual code (fixing the
mismatch was safe because nothing else in the repository referenced the
old filename; verified with a repository-wide search before renaming).

| Old path | New path | Notes |
|---|---|---|
| `asset/js/operations/NFC_Tap-to-Authenticate.js` | `security/nfc/NFC_Tap-to-Authenticate.js` | No change other than location. |
| `asset/js/ferensics/VioceAndRadioCodeTelemetry.js` (note: filename had a trailing space) | `security/voice/VoiceAndRadioCodeTelemetry.js` | Fixed "Vioce" → "Voice" typo and removed the trailing space in the filename. No other file referenced the old name (verified via repo-wide grep). |
| `asset/java/SecureTrustAndForensicGateway.java` (contained class `VoiceBiometricGatekeeper`) | `security/voice/VoiceBiometricGatekeeper.java` | Filename now matches the public class it contains. |
| `asset/java/passkey.java` (contained class `SecureTrustAndForensicGateway`, incl. `verifyPasskeySignature`) | `security/auth/SecureTrustAndForensicGateway.java` | Filename now matches the public class it contains. |
| `asset/java/admin-police.java` (class `PoliceEvidenceFirewall`) | `security/auth/PoliceEvidenceFirewall.java` | Filename now matches the public class. |
| `asset/java/admin-fire.java` (class `SecureAssetFirewall`) | `security/auth/SecureAssetFirewall.java` | Filename now matches the public class. |
| `asset/java/security-filter.java` (class `SecurityCoreUtils`) | `security/auth/SecurityCoreUtils.java` | Filename now matches the public class. |
| `asset/java/security-ran-key-generator.java` (class `SecureTokenGenerator`) | `security/auth/SecureTokenGenerator.java` | Filename now matches the public class. |
| `asset/java/legacy-trust-login.java` (class `SecurityFilter`) | `security/auth/SecurityFilter.java` | Filename now matches the public class. |
| `asset/java/secure-authenication-logic.java` (class `LoginServlet`) | `security/auth/LoginServlet.java` | Filename now matches the public class; also fixes the "authenication" typo by dropping it from the new name. |
| `asset/java/KeyGenParameterSpec.java` | `security/auth/android/KeyGenParameterSpec.java` | Code fragment (not a full class); moved under an `android/` subfolder since it is Android/Keystore-specific. |
| `asset/cpp/src/CameraInterface.h` | `security/native/camera/include/CameraInterface.h` | Kept as the canonical interface (it was the more complete of two duplicate copies — see below). |
| `asset/cpp/include/CameraInterface.h` | *(removed, duplicate)* | This was an older/incomplete duplicate of `asset/cpp/src/CameraInterface.h` (missing `maxWidth`/`maxHeight`/`maxFPS` fields on `CameraInfo`). Removed in favor of the single canonical header above. Nothing included it via its `asset/cpp/include/` path directly (compilers resolved the quoted `#include "CameraInterface.h"` relative to the including file's own directory). |
| `asset/cpp/src/CameraFactory.h` | `security/native/camera/include/CameraFactory.h` | No change other than location. |
| `asset/cpp/include/Platform.h` | `security/native/camera/include/Platform.h` | No change other than location. |
| `asset/cpp/android/AndroidCamera.cpp` | `security/native/camera/android/AndroidCamera.cpp` | No change other than location. |
| `asset/cpp/src/native_camera.cpp` | `security/native/camera/android/native_camera.cpp` | Grouped with the other Android camera backend since it is also Android NDK Camera-Manager code. |
| `asset/cpp/ios/IOSCamera.mm` | `security/native/camera/ios/IOSCamera.mm` | No change other than location. |
| `asset/cpp/linux/LinuxCamera.cpp` | `security/native/camera/linux/LinuxCamera.cpp` | No change other than location. |

A new `security/native/camera/CMakeLists.txt` was added (the old
`asset/cpp/CMakeLists.txt`, which covers unrelated audio-only targets and
was already broken/duplicated pre-existing content, was left in place
unmodified since it does not reference any of the moved files).

## Files intentionally left in place

The following were searched for as candidates but intentionally **not**
moved, because they are not biometric/auth/security-boundary code:

* `asset/js/hardwareBridge.js` / `asset/cpp/src/hardware_bridge.cpp` —
  thermal *sensor* bridge (temperature telemetry), not biometric auth.
* `asset/js/operations/WebXR-Camera.js` — an AR distance-measurement tool,
  not face/gait capture or authentication.
* `asset/js/securety/signature.js` — despite living in a misspelled
  "securety" folder, this file is NFT asset metadata, not security code.
* `asset/java/masked-api.java`, `asset/java/keymask.java`,
  `asset/java/image-covert.java` — generic utility helpers (URL printer,
  generic string masking, raw file-to-bytes conversion) with no
  biometric/auth-specific logic.
* `asset/java/MobileEnvironmentDispatcher.java`,
  `asset/java/BadgeAssignmentController.java` — OS-detection dispatch and
  badge-assignment business logic, not security/auth boundary code.

## Known pre-existing gap (not introduced by this change)

`.github/workflows/organize-assets.yml` runs `javac SecureAssetFirewall.java`
/ `java SecureAssetFirewall` expecting a file at the **repository root**.
That file never existed at the root before this change (the `SecureAssetFirewall`
class previously lived at `asset/java/admin-fire.java`, now at
`security/auth/SecureAssetFirewall.java`), so this workflow step was already
broken prior to this reorganization and remains unaffected by it.

## Deployment commands (quick reference)

```bash
# Docker (recommended)
cp security/.env.example security/.env   # then edit real values
./security/deploy.sh

# systemd (see security/trust-security.service header for full steps)
sudo systemctl enable --now trust-security

# Local dev
cd security && npm install && npm start

# Smoke test
cd security && npm test

# Native camera module (Linux backend smoke build)
cmake -S security/native/camera -B /tmp/security-camera-build
cmake --build /tmp/security-camera-build
```
