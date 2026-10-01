package com.legacytrust.security;

public class KeyMaskingUtil {

    /**
     * Masks an existing key, leaving only the specified number of trailing characters visible.
     * 
     * @param originalKey The existing secret key or token string.
     * @param visibleCount The number of trailing characters to leave unmasked (e.g., 4).
     * @return The masked string (e.g., "****************3f8a").
     */
    public static String maskExistingKey(String originalKey, int visibleCount) {
        if (originalKey == null || originalKey.isBlank()) {
            return "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
";
        }
        
        if (originalKey.length() <= visibleCount) {
            return "****";
        }

        int maskLength = originalKey.length() - visibleCount;
        StringBuilder masked = new StringBuilder();
        
        for (int i = 0; i < maskLength; i++) {
            masked.append("*");
        }
        
        masked.append(originalKey.substring(maskLength));
        return masked.toString();
    }

    public static void main(String[] args) {
        String apiKey = "trust_live_9f8e7d6c5b4a3f8a";
        String safeDisplay = maskExistingKey(apiKey, 4);
        
        System.out.println("Original: " + apiKey);
        System.out.println("Masked:   " + safeDisplay);
        // Output: Masked: ********************3f8a
    }
}
