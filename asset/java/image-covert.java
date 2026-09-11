import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class ImageBinaryConverter {

    public static byte[] convertImageToBinary(Path imagePath) throws IOException {
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
