package com.legacytrust.security;

import java.security.SecureRandom;
import java.util.Base64;

public class SecureTokenGenerator {

    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    private static final Base64.Encoder URL_ENCODER = Base64.getUrlEncoder().withoutPadding();

    /**
     * Generates a cryptographically secure, URL-safe random token.
     * 
     * @param byteLength The number of random bytes (e.g., 32 bytes = 256 bits of entropy).
     * @return The encoded token string.
     */
    public static String generateToken(int byteLength) {
        byte[] randomBytes = new byte[byteLength];
        SECURE_RANDOM.nextBytes(randomBytes);
        return URL_ENCODER.encodeToString(randomBytes);
    }

    public static void main(String[] args) {
        // Example: Generate a 32-byte (256-bit) secure administration token
        String adminToken = generateToken(32);
        System.out.println("Generated Secure Token: " + adminToken);
    }
}
