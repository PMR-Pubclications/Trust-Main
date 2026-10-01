// Java / Android native key generation requiring biometric confirmation
KeyGenParameterSpec keyGenParameterSpec = new KeyGenParameterSpec.Builder(
    "TrustSecureKey",
    KeyProperties.PURPOSE_SIGN | KeyProperties.PURPOSE_VERIFY)
    .setDigests(KeyProperties.DIGEST_SHA256)
    .setUserAuthenticationRequired(true) // Forces biometric auth (fingerprint/face)
    .setUserAuthenticationValidityDurationSeconds(10) // Window before re-auth is required
    .setIsStrongBoxBacked(true) // Enforces hardware security module if available
    .build();
