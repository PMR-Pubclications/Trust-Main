package com.police.forensics.security;

import java.io.IOException;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;

public class PoliceEvidenceFirewall {

    public enum ClearanceLevel {
        PUBLIC,
        FIELD_OFFICER,
        DETECTIVE_INVESTIGATOR,
        FORENSIC_ANALYST,
        EVIDENCE_CUSTODIAN,
        COMMAND_STAFF
    }

    private static final Map<String, ClearanceLevel> EVIDENCE_CLEARANCE = Map.of(
        "crime_scene_media", ClearanceLevel.FIELD_OFFICER,
        "dispatch_logs", ClearanceLevel.DETECTIVE_INVESTIGATOR,
        "digital_evidence", ClearanceLevel.FORENSIC_ANALYST,
        "forensic_reports", ClearanceLevel.FORENSIC_ANALYST,
        "restricted_evidence", ClearanceLevel.COMMAND_STAFF
    );

    public static boolean verifyChainOfCustodyAuthorization(byte[] biometricSignature, ClearanceLevel requiredLevel, ClearanceLevel userLevel) {
        if (biometricSignature == null || biometricSignature.length == 0) {
            System.err.println("Chain of Custody Alert: Biometric signature missing or invalid. Access rejected.");
            return false;
        }
        return userLevel.ordinal() >= requiredLevel.ordinal();
    }

    public static String generateEvidenceHash(Path file) throws IOException, NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] fileBytes = Files.readAllBytes(file);
        byte[] hashBytes = digest.digest(fileBytes);
        StringBuilder sb = new StringBuilder();
        for (byte b : hashBytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    public static void intakeEvidenceItem(Path sourceFile, Path evidenceVaultBase, ClearanceLevel currentAnalystLevel, byte[] biometricToken) {
        try {
            String fileName = sourceFile.getFileName().toString();
            String lowerName = fileName.toLowerCase();

            String category = determineEvidenceCategory(lowerName);
            ClearanceLevel requiredLevel = EVIDENCE_CLEARANCE.getOrDefault(category, ClearanceLevel.COMMAND_STAFF);

            if (!verifyChainOfCustodyAuthorization(biometricToken, requiredLevel, currentAnalystLevel)) {
                System.err.println("Intake Denied: Insufficient clearance or invalid biometric token for evidence item -> " + fileName);
                return;
            }

            // Generate cryptographic integrity hash for court admissibility
            String fileHash = generateEvidenceHash(sourceFile);
            System.out.println("Chain of Custody Integrity Hash (SHA-256): " + fileHash);

            Path targetSubDir = evidenceVaultBase.resolve(category);
            if (!Files.exists(targetSubDir)) {
                Files.createDirectories(targetSubDir);
            }

            Path targetFile = targetSubDir.resolve(sourceFile.getFileName());
            // Copy (or move) while preserving master artifact integrity
            Files.copy(sourceFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
            
            System.out.println("Evidence Securely Vaulted: " + fileName + " archived into vault/" + category + "/ [Hash Recorded]");

        } catch (IOException | NoSuchAlgorithmException e) {
            System.err.println("Evidence intake failure: " + e.getMessage());
        }
    }

    private static String determineEvidenceCategory(String lowerName) {
        if (lowerName.endsWith(".e01") || lowerName.endsWith(".dd") || lowerName.endsWith(".raw") || lowerName.contains("extraction") || lowerName.contains("dump")) {
            return "digital_evidence";
        }
        if (lowerName.endsWith(".mp4") || lowerName.endsWith(".mov") || lowerName.endsWith(".jpg") || lowerName.endsWith(".png") || lowerName.contains("cctv") || lowerName.contains("bodycam")) {
            return "crime_scene_media";
        }
        if (lowerName.contains("report") || lowerName.contains("analysis") || lowerName.contains("ballistics") || lowerName.contains("latent")) {
            return "forensic_reports";
        }
        if (lowerName.contains("dispatch") || lowerName.contains("cad") || lowerName.contains("911")) {
            return "dispatch_logs";
        }
        return "restricted_evidence";
    }
}
