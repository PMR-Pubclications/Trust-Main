package com.legacytrust.controller;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.Map;

@RestController
@RequestMapping("/api/trust/badges")
public class BadgeAssignmentController {

    private final DataSource dataSource;

    public BadgeAssignmentController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @PostMapping("/assign")
    public ResponseEntity<?> assignCardToAgent(@RequestBody Map<String, String> payload, HttpServletRequest request) {
        // Ensure only authenticated admins can assign credentials
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("adminUser") == null) {
            return ResponseEntity.status(401).body(Map.of("status", "error", "message", "Unauthorized access."));
        }

        String cardUid = payload.get("cardUid");
        String targetUsername = payload.get("username");

        if (cardUid == null || targetUsername == null || cardUid.isBlank() || targetUsername.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("status", "error", "message", "Card UID and agent username are required."));
        }

        // Upsert logic: Links card UID to user, reassigns if card was previously used
        String sql = "INSERT INTO agency_rfid_badges (card_uid, admin_id, is_active) " +
                     "SELECT ?, admin_id, TRUE FROM legacy_trust_admins WHERE username = ? " +
                     "ON DUPLICATE KEY UPDATE admin_id = VALUES(admin_id), is_active = TRUE, assigned_at = CURRENT_TIMESTAMP";

        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, cardUid.trim());
            pstmt.setString(2, targetUsername.trim());
            int affectedRows = pstmt.executeUpdate();

            if (affectedRows > 0) {
                return ResponseEntity.ok(Map.of("status", "success", "message", "RFID badge successfully assigned to " + targetUsername));
            } else {
                return ResponseEntity.status(404).body(Map.of("status", "error", "message", "Target agent username not found in database."));
            }

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("status", "error", "message", "Database error during card assignment."));
        }
    }
}
