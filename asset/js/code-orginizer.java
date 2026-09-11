import java.io.IOException;
import java.nio.file.*;
import java.util.Map;
import java.util.stream.Stream;

public class AssetOrganizer {

    private static final Path ROOT_DIR = Paths.get(".");
    private static final Path ASSETS_BASE = Paths.get("assets");

    // Map file extensions to their respective destination subdirectories inside assets/
    private static final Map<String, String> EXTENSION_MAP = Map.ofEntries(
        Map.entry(".js", "js"),
        Map.entry(".py", "python"),
        Map.entry(".php", "php"),
        Map.entry(".json", "json"),
        Map.entry(".sh", "bash"),
        Map.entry(".html", "html"),
        Map.entry(".htm", "html")
    );

    public static void organizeAssets() {
        try {
            // Ensure the base assets directory exists
            if (!Files.exists(ASSETS_BASE)) {
                Files.createDirectories(ASSETS_BASE);
            }

            // Scan the root directory files directly
            try (Stream<Path> paths = Files.list(ROOT_DIR)) {
                paths.filter(Files::isRegularFile)
                     .forEach(sourceFile -> {
                         String fileNameStr = sourceFile.getFileName().toString();
                         String lowerName = fileNameStr.toLowerCase();

                         // Prevent the organizer script from cleaning itself up
                         if (lowerName.equals("assetorganizer.java") || lowerName.equals("assetorganizer.class")) {
                             return;
                         }

                         // Check file extension and route to the correct asset folder
                         for (Map.Entry<String, String> entry : EXTENSION_MAP.entrySet()) {
                             if (lowerName.endsWith(entry.getKey())) {
                                 try {
                                     Path targetSubDir = ASSETS_BASE.resolve(entry.getValue());
                                     if (!Files.exists(targetSubDir)) {
                                         Files.createDirectories(targetSubDir);
                                     }

                                     Path targetFile = targetSubDir.resolve(sourceFile.getFileName());
                                     
                                     // Move file, overwrite if it exists in target, and clean from root
                                     Files.move(sourceFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
                                     System.out.println("Organized: " + fileNameStr + " -> assets/" + entry.getValue() + "/");
                                 } catch (IOException e) {
                                     System.err.println("Failed to move file " + fileNameStr + ": " + e.getMessage());
                                 }
                                 break;
                             }
                         }
                     });
            }
            
            System.out.println("Asset organization and cleanup complete.");
        } catch (IOException e) {
            System.err.println("Error accessing directories: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        organizeAssets();
    }
}
