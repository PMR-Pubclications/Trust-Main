package com.legacy.security;

import java.io.IOException;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Map;

public class AgencyReportRouterGateway {

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

    public static boolean evaluateAgencyBoundary(ClearanceRole role, AgencyDomain targetDomain, byte[] authData, byte[] signature, PublicKey publicKey) {
        if (!verifyPasskeySignature(authData, signature, publicKey)) {
            System.err.println("Gateway Breach Alert: Hardware passkey signature verification failed.");
            return false;
        }

        switch (targetDomain) {
            case LEGACY_TRUST:
                return role == ClearanceRole.TRUST_ADMINISTRATOR || role == ClearanceRole.COMMAND_STAFF;
            case FIRE_AGENCY:
                return role == ClearanceRole.FIRE_RESPONDER || role == ClearanceRole.COMMAND_STAFF;
            case POLICE_AGENCY:
                return role == ClearanceRole.POLICE_OFFICER || role == ClearanceRole.COMMAND_STAFF;
            default:
                System.err.println("Security Firewall Violation: Unauthorized crossover attempt.");
                return false;
        }
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

    public static void ingestAndRouteReport(Path sourceFile, Path repoBaseRoot, ClearanceRole role, byte[] authData, byte[] signature, PublicKey publicKey, Connection dbConnection) {
        try {
            String fileName = sourceFile.getFileName().toString();
            String lowerName = fileName.toLowerCase();

            AgencyDomain targetDomain = determineAgencyDomain(lowerName);

            if (!evaluateAgencyBoundary(role, targetDomain, authData, signature, publicKey)) {
                System.err.println("Gateway Gatekeeper: Transfer aborted due to jurisdictional boundary or biometric authentication failure for -> " + fileName);
                return;
            }

            // Map target folders directly to your GitHub repository paths structure
            String subFolderPath = getAgencyRepositoryPath(targetDomain);
            Path targetSubDir = repoBaseRoot.resolve(subFolderPath);

            if (!Files.exists(targetSubDir)) {
                Files.createDirectories(targetSubDir);
            }

            String auditHash = generateAuditHash(sourceFile);
            Path targetFile = targetSubDir.resolve(sourceFile.getFileName());
            
            Files.copy(sourceFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
            
            // Log ingestion into the respective database backend
            logReportToDatabase(dbConnection, targetDomain, fileName, targetFile.toString(), auditHash, role.toString());
            
            System.out.println("Gateway Cleared: [Agency: " + targetDomain + "] Report securely vaulted to " + subFolderPath + ". SHA-256 Hash: " + auditHash);

        } catch (IOException | NoSuchAlgorithmException | SQLException e) {
            System.err.println("Agency report routing failure: " + e.getMessage());
        }
    }

    private static AgencyDomain determineAgencyDomain(String lowerName) {
        if (lowerName.contains("trust") || lowerName.contains("legacy") || lowerName.contains("foster") || lowerName.contains("campus") || lowerName.contains("ledger")) {
            return AgencyDomain.LEGACY_TRUST;
        }
        if (lowerName.contains("fire") || lowerName.contains("hazmat") || lowerName.contains("incident_f") || lowerName.contains("dispatch_f")) {
            return AgencyDomain.FIRE_AGENCY;
        }
        if (lowerName.contains("police") || lowerName.contains("dispatch") || lowerName.contains("evidence") || lowerName.contains("cad") || lowerName.contains("bodycam") || lowerName.contains("ballistics")) {
            return AgencyDomain.POLICE_AGENCY;
        }
        return AgencyDomain.UNAUTHORIZED_CROSSOVER;
    }

    private static String getAgencyRepositoryPath(AgencyDomain domain) {
        switch (domain) {
            case LEGACY_TRUST:
                return "asset/SQL/agencies/LegacyTrust";
            case FIRE_AGENCY:
                return "asset/SQL/agencies/fire";
            case POLICE_AGENCY:
                return "asset/SQL/agencies/police";
            default:
                return "asset/SQL/agencies/unauthorized";
        }
    }

    private static void logReportToDatabase(Connection conn, AgencyDomain domain, String fileName, String filePath, String sha256Hash, String submitterRole) throws SQLException {
        if (conn == null) return;
        
        String tableName = "";
        switch (domain) {
            case LEGACY_TRUST: tableName = "legacy_trust_reports"; break;
            case FIRE_AGENCY: tableName = "fire_agency_reports"; break;
            case POLICE_AGENCY: tableName = "police_agency_reports"; break;
            default: return;
        }

        String sql = "INSERT INTO " + tableName + " (file_name, file_path, sha256_hash, submitter_role, intake_timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, fileName);
            pstmt.setString(2, filePath);
            pstmt.setString(3, sha256Hash);
            pstmt.setString(4, submitterRole);
            pstmt.executeUpdate();
        }
    }
}
