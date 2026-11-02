package com.ballistics;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;
import java.util.logging.ConsoleHandler;
import java.util.logging.FileHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Main {
    private static final Logger LOGGER = Logger.getLogger(Main.class.getName());
    private static final String DEFAULT_CONFIG = "/etc/ballistics-video-analysis/application.properties";

    public static void main(String[] args) throws IOException {
        Properties properties = loadProperties();
        int port = integerProperty(properties, "server.port", "BALLISTICS_PORT", 9090);
        int logLimit = integerProperty(properties, "logging.max-bytes", "BALLISTICS_LOG_MAX_BYTES", 10 * 1024 * 1024);
        int logCount = integerProperty(properties, "logging.file-count", "BALLISTICS_LOG_FILE_COUNT", 5);
        String logPattern = stringProperty(properties, "logging.file", "BALLISTICS_LOG_FILE",
                "logs/ballistics-%g.log");
        configureLogging(logPattern, logLimit, logCount);

        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("server.port must be between 1 and 65535");
        }

        try (ServerSocket serverSocket = new ServerSocket()) {
            serverSocket.setReuseAddress(true);
            serverSocket.bind(new InetSocketAddress(port));
            LOGGER.info(() -> "Ballistic video analysis server listening on port " + port);
            while (true) {
                Socket client = serverSocket.accept();
                try (client; InputStream input = client.getInputStream()) {
                    LOGGER.info(() -> "Accepted video feed connection from " + client.getRemoteSocketAddress());
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    while ((bytesRead = input.read(buffer)) != -1) {
                        processFrameData(buffer, bytesRead);
                    }
                } catch (IOException e) {
                    LOGGER.log(Level.WARNING, "Video feed connection failed", e);
                }
            }
        }
    }

    private static Properties loadProperties() throws IOException {
        Properties properties = new Properties();
        String configPath = System.getProperty("ballistics.config",
                System.getenv().getOrDefault("BALLISTICS_CONFIG", DEFAULT_CONFIG));
        Path path = Path.of(configPath);
        if (Files.exists(path)) {
            try (InputStream input = Files.newInputStream(path)) {
                properties.load(input);
            }
        }
        return properties;
    }

    private static int integerProperty(Properties properties, String key, String environmentName, int defaultValue) {
        String value = stringProperty(properties, key, environmentName, Integer.toString(defaultValue));
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(key + " must be an integer", e);
        }
    }

    private static String stringProperty(Properties properties, String key, String environmentName,
                                         String defaultValue) {
        String value = System.getProperty(key);
        if (value == null || value.isBlank()) {
            value = System.getenv(environmentName);
        }
        if (value == null || value.isBlank()) {
            value = properties.getProperty(key, defaultValue);
        }
        return value;
    }

    private static void configureLogging(String pattern, int limit, int count) throws IOException {
        if (limit <= 0 || count <= 0) {
            throw new IllegalArgumentException("logging.max-bytes and logging.file-count must be positive");
        }
        Path logFile = Path.of(pattern);
        Path parent = logFile.toAbsolutePath().getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }

        LOGGER.setUseParentHandlers(false);
        for (Handler handler : LOGGER.getHandlers()) {
            LOGGER.removeHandler(handler);
            handler.close();
        }
        ConsoleHandler console = new ConsoleHandler();
        console.setLevel(Level.INFO);
        LOGGER.addHandler(console);
        FileHandler file = new FileHandler(pattern, limit, count, true);
        file.setLevel(Level.INFO);
        LOGGER.addHandler(file);
        LOGGER.setLevel(Level.INFO);
    }

    private static void processFrameData(byte[] data, int length) {
        // Pass incoming frame bytes to the Java tracking engine.
    }
}
