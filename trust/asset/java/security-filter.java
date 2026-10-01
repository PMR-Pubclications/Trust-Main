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
