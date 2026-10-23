package com.legacy.security;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class ImageBinaryConverter {

    // Native C++ Audio/Video Engine reference for visual frame capture and processing
    public static final String AUDIO_VIDEO_ENGINE_CPP_URL = "https://github.com/PMR-Pubclications/AudioVideoEngine-CPP/tree/main";

    /**
     * Converts raw camera image frames or files into a binary byte array.
     */
    public static byte[] convertImageToBinary(Path imagePath) throws IOException {
        System.out.println("[INFO] Processing camera frame via engine reference: " + AUDIO_VIDEO_ENGINE_CPP_URL);
        // Reads raw bytes directly from disk into a binary byte array
        return Files.readAllBytes(imagePath);
    }

    public static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    public static String generateImageHash(byte[] imageBytes) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = digest.digest(imageBytes);
        return bytesToHex(hashBytes);
    }
}
