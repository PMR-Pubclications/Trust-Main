package com.legacy.security;

import java.io.IOException;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.util.Map;

public class SecureTrustAndForensicGateway {

    public enum SystemDomain {
        TRUST_ADMINISTRATION,
        FIRST_RESPONDER_OPS,
        UNAUTHORIZED_CROSSOVER
    }

    public enum ClearanceRole {
        TRUST_TRUSTEE,
        TRUST_AUDITOR,
        FIELD_OFFICER,
        DETECTIVE_INVESTIGATOR,
        FORENSIC_ANALYST,
        EVIDENCE_CUSTODIAN,
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

    public static boolean evaluateDomainBoundary(ClearanceRole role, SystemDomain targetDomain, byte[] authData, byte[] signature, PublicKey publicKey) {
        // Enforce hardware-backed passkey/biometric cryptographic verification before checking domain access
        if (!verifyPasskeySignature(authData, signature, publicKey)) {
            System.err.println("Gateway Breach Alert: Hardware passkey signature verification failed.");
            return false;
        }

        boolean isTrustPersonnel = (role == ClearanceRole.TRUST_TRUSTEE || role == ClearanceRole.TRUST_AUDITOR);
        boolean isResponderPersonnel = (role == ClearanceRole.FIELD_OFFICER || role == ClearanceRole.DETECTIVE_INVESTIGATOR || 
                                      role == ClearanceRole.FORENSIC_ANALYST || role == ClearanceRole.EVIDENCE_CUSTODIAN || 
                                      role == ClearanceRole.COMMAND_STAFF);

        // Absolute Air-Gap / Isolation Check between Trusts and Responders
        if (targetDomain == SystemDomain.TRUST_ADMINISTRATION && !isTrustPersonnel) {
            System.err.println("Security Firewall Violation: Non-trust personnel attempted unauthorized ingress into Trust Administration domain.");
            return false;
        }

        if (targetDomain == SystemDomain.FIRST_RESPONDER_OPS && !isResponderPersonnel && role != ClearanceRole.TRUST_AUDITOR) {
            System.err.println("Security Firewall Violation: Unauthorized role attempted ingress into First Responder operational domain.");
            return false;
        }

        return true;
    }

    public static String generateAuditHash(Path file) throws IOException, NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] fileBytes = Files.readAllBytes(file);
        byte[] hashBytes = digest.digest(fileBytes);
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    public static void routeAndIsolateAsset(Path sourceFile, Path secureVaultRoot, ClearanceRole role, byte[] authData, byte[] signature, PublicKey publicKey) {
        try {
            String fileName = sourceFile.getFileName().toString();
            String lowerName = fileName.toLowerCase();

            SystemDomain targetDomain = determineTargetDomain(lowerName);

            if (!evaluateDomainBoundary(role, targetDomain, authData, signature, publicKey)) {
                System.err.println("Gateway Gatekeeper: Transfer aborted due to jurisdictional domain or biometric authentication failure for -> " + fileName);
                return;
            }

            String category = determineSubCategory(lowerName, targetDomain);
            String domainFolder = (targetDomain == SystemDomain.TRUST_ADMINISTRATION) ? "trust_vault" : "responder_vault";
            Path targetSubDir = secureVaultRoot.resolve(domainFolder).resolve(category);

            if (!Files.exists(targetSubDir)) {
                Files.createDirectories(targetSubDir);
            }

            // Generate tamper-evident cryptographic SHA-256 hash for court admissibility or trust ledger integrity
            String auditHash = generateAuditHash(sourceFile);
            Path targetFile = targetSubDir.resolve(sourceFile.getFileName());
            
            Files.copy(sourceFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("Gateway Cleared: [" + targetDomain + " -> " + category + "] Asset securely vaulted. SHA-256 Hash: " + auditHash);

        } catch (IOException | NoSuchAlgorithmException e) {
            System.err.println("Gateway routing error: " + e.getMessage());
        }
    }

    private static SystemDomain determineTargetDomain(String lowerName) {
        if (lowerName.contains("trust") || lowerName.contains("legacy") || lowerName.contains("foster") || lowerName.contains("campus") || lowerName.contains("ledger") || lowerName.contains("bylaws")) {
            return SystemDomain.TRUST_ADMINISTRATION;
        }
        if (lowerName.contains("dispatch") || lowerName.contains("evidence") || lowerName.contains("cad") || lowerName.contains("bodycam") || lowerName.contains("incident") || lowerName.contains("forensic") || lowerName.contains("ballistics")) {
            return SystemDomain.FIRST_RESPONDER_OPS;
        }
        return SystemDomain.UNAUTHORIZED_CROSSOVER;
    }

    private static String determineSubCategory(String lowerName, SystemDomain domain) {
        if (domain == SystemDomain.TRUST_ADMINISTRATION) {
            if (lowerName.contains("ledger") || lowerName.contains("financial")) return "financial_ledgers";
            if (lowerName.contains("foster") || lowerName.contains("campus")) return "foster_campus_development";
            return "trust_governance";
        } else {
            if (lowerName.endsWith(".e01") || lowerName.endsWith(".dd") || lowerName.contains("extraction")) return "digital_evidence";
            if (lowerName.endsWith(".mp4") || lowerName.endsWith(".mov") || lowerName.contains("cctv") || lowerName.contains("bodycam")) return "crime_scene_media";
            if (lowerName.contains("report") || lowerName.contains("ballistics") || lowerName.contains("latent")) return "forensic_reports";
            if (lowerName.contains("dispatch") || lowerName.contains("cad") || lowerName.contains("911")) return "dispatch_logs";
            return "restricted_evidence";
        }
    }
}
