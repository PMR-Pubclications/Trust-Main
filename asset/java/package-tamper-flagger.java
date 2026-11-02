import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.util.Base64;

public class LivePackageTamperServer {

    private static final String SECRET_KEY = "YOUR_SUPER_SECRET_HMAC_KEY";

    public static void main(String[] args) throws IOException {
        // Bind an embedded HTTP server to listen for real sensor/gateway webhooks (Port 8080)
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/api/package/telemetry", new PackageWebhookHandler());
        server.setExecutor(null); // creates a default executor
        System.out.println("Live Package Forensic Server started on port 8080...");
        server.start();
    }

    static class PackageWebhookHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equals(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
                return;
            }

            // 1. Capture Real Source IP Address of the IoT sensor/gateway caller
            InetSocketAddress remoteAddress = exchange.getRemoteAddress();
            String sourceIpAddress = remoteAddress.getAddress().getHostAddress();

            // 2. Extract Headers for Cryptographic Verification (Anti-Tamper/Anti-Spoofing)
            String hmacSignature = exchange.getRequestHeaders().getFirst("X-Signature-HMAC");
            String trackingNumber = exchange.getRequestHeaders().getFirst("X-Tracking-Number");
            String statusFlag = exchange.getRequestHeaders().getFirst("X-Package-Status"); // "SECURE" or "TAMPERED"

            // Read request body (if payload validation is required)
            byte[] requestBody = exchange.getRequestBody().readAllBytes();

            // 3. Verify Request Authenticity using HMAC
            if (!verifyHmac(requestBody, hmacSignature)) {
                String response = "Unauthorized: Invalid cryptographic signature.";
                exchange.sendResponseHeaders(401, response.length());
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(response.getBytes());
                }
                return;
            }

            boolean isTampered = "TAMPERED".equalsIgnoreCase(statusFlag);
            LocalDateTime timestamp = LocalDateTime.now();

            // 4. Process real event logic
            if (isTampered) {
                triggerRealAlert(trackingNumber, timestamp, sourceIpAddress);
            } else {
                System.out.println("[INFO] Package " + trackingNumber + " verified intact from IP: " + sourceIpAddress);
            }

            // Send HTTP 200 OK back to the scanning device/gateway
            String response = "Event processed successfully.";
            exchange.sendResponseHeaders(200, response.length());
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes());
            }
        }

        private boolean verifyHmac(byte[] payload, String receivedSignature) {
            if (receivedSignature == null) return false;
            try {
                Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
                SecretKeySpec secret_key = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
                sha256_HMAC.init(secret_key);
                byte[] hash = sha256_HMAC.doFinal(payload);
                String computedSignature = Base64.getEncoder().encodeToString(hash);
                return computedSignature.equals(receivedSignature);
            } catch (NoSuchAlgorithmException | InvalidKeyException e) {
                return false;
            }
        }

        private void triggerRealAlert(String trackingNumber, LocalDateTime time, String ip) {
            String alertMessage = String.format(
                "CRITICAL SECURITY ALERT: Package %s flagged as TAMPERED! Breach timestamp: %s, Origin IP: %s",
                trackingNumber, time, ip
            );
            
            // TODO: Wire this into a real notification channel (e.g., Twilio API for SMS, Java Mail API, or FCM)
            System.err.println("\n>>> [DISPATCHING LIVE ALERT TO RECEIVER] <<<");
            System.err.println(alertMessage);
        }
    }
}
