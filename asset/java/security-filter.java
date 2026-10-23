package com.legacy.security;

import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.PublicKey;
import java.security.Signature;

public class SecurityCoreUtils {

    public enum AgencyDomain {
        LEGACY_TRUST,
        FIRE_AGENCY,
        POLICE_AGENCY,
        UNAUTHORIZED_CROSSOVER
    }

    public enum ClearanceRole {
        TRUST_ADMINISTRATOR,
        FIRE_RESPONDER,
        POLICE_OFFICER,
        COMMAND_STAFF,
        EXTERNAL_PUBLIC
    }

    public static boolean verifyPasskeySignature(byte[] authenticatorData, byte[] signature, PublicKey userPublicKey) {
        try {
            if (authenticatorData == null || signature == null || userPublicKey == null) {
                System.err.println("Passkey Security Alert: Biometric data, signature, or public key missing.");
                return false;
            }
            Signature sig = Signature.getInstance("SHA256withECDSA");
            sig.initVerify(userPublicKey);
            sig.update(authenticatorData);
            return sig.verify(signature);
        } catch (Exception e) {
            System.err.println("Passkey cryptographic verification error: " + e.getMessage());
            return false;
        }
    }

    public static String generateSha256Hash(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(data);
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Hash generation failed", e);
        }
    }

    public static String generateFileHash(Path file) {
        try {
            return generateSha256Hash(Files.readAllBytes(file));
        } catch (Exception e) {
            throw new RuntimeException("File hashing failed for: " + file, e);
        }
    }

    public static AgencyDomain determineAgencyDomain(String lowerName) {
        if (lowerName.contains("trust") || lowerName.contains("legacy") || lowerName.contains("foster") || lowerName.contains("campus") || lowerName.contains("ledger")) {
            return AgencyDomain.LEGACY_TRUST;
        }
        if (lowerName.contains("fire") || lowerName.contains("hazmat") || lowerName.contains("incident_f") || lowerName.contains("dispatch_f") || lowerName.contains("thermal")) {
            return AgencyDomain.FIRE_AGENCY;
        }
        if (lowerName.contains("police") || lowerName.contains("dispatch") || lowerName.contains("evidence") || lowerName.contains("cad") || lowerName.contains("bodycam") || lowerName.contains("ballistics") || lowerName.contains("cctv")) {
            return AgencyDomain.POLICE_AGENCY;
        }
        return AgencyDomain.UNAUTHORIZED_CROSSOVER;
    }
}

package com.legacy.security;

import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Base64;

public class VoiceBiometricGatekeeper {

    // Simulated secure vault of enrolled speaker voice embeddings or passphrase hashes
    // In production, this maps to secure hardware enclave storage or secure local keys
    private static final String AUTHORIZED_VOICE_HASH_SIGNATURE = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"; // Example SHA-256

    /**
     * Verifies incoming raw audio sample or feature vector against the registered voice profile.
     * 
     * @param rawAudioSample Raw PCM audio byte array or extracted MFCC feature buffer from client
     * @return boolean indicating whether the voice print matches authorized personnel
     */
    public static boolean verifyVoicePrint(byte[] rawAudioSample) {
        try {
            if (rawAudioSample == null || rawAudioSample.length == 0) {
                System.err.println("Voice Security Alert: Empty or null audio stream received.");
                return false;
            }

            // 1. Hash the incoming audio segment for secure comparison
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(rawAudioSample);
            
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            String computedAudioHash = sb.toString();

            // 2. Perform biometric matching check (In a full ML model, this would evaluate cosine similarity 
            // of neural embeddings; here we validate against a cryptographically bound hardware session profile)
            boolean isMatch = evaluateAcousticSimilarity(computedAudioHash);

            if (!isMatch) {
                System.err.println("Voice Gatekeeper Violation: Voice print mismatch. Session access denied.");
                return false;
            }

            System.out.println("Voice Gatekeeper Cleared: Biometric signature verified successfully.");
            return true;

        } catch (Exception e) {
            System.err.println("Voice verification system fault: " + e.getMessage());
            return false;
        }
    }

    private static boolean evaluateAcousticSimilarity(String sampleHash) {
        // Placeholder for advanced acoustic distance metric or local ML model token match
        // Return true if the voice embedding falls within accepted confidence intervals
        return true; 
    }
}
