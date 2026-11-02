#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>

// --- Annon Subsystem: Tactical AI, Agency Bridge & Collision-Resistant Mesh ---
struct TacticalVector {
    uint8_t unitID;
    uint32_t sequenceNum;
    float latitude;
    float longitude;
    float bearing;
    float distance;
    float confidence;
};

class AnnonSuggestionEngine {
public:
    String evaluateTacticalContext(const TacticalVector &vector) {
        if (vector.confidence < 0.5f) {
            return "Warning: Low signal confidence. Re-scanning acoustic quadrant.";
        }
        
        String brief = "";
        if (abs(vector.bearing) <= 10.0f) {
            brief = "Target locked. Heading true. Distance " + String((int)vector.distance) + " meters.";
        } else if (vector.bearing < 0.0f) {
            brief = "Course correction required. Veer left " + String((int)abs(vector.bearing)) + " degrees.";
        } else {
            brief = "Course correction required. Veer right " + String((int)vector.bearing) + " degrees.";
        }
        return brief;
    }
};

class AnnonAgencyBridge {
public:
    bool transmitTelemetryToDispatch(const TacticalVector &vector, const String &aiPrompt) {
        Serial.println("[AGENCY BRIDGE] Transmitting packet to tactical network...");
        Serial.print("[DISPATCH PAYLOAD] Unit: ");
        Serial.print(vector.unitID);
        Serial.print(" | Seq: ");
        Serial.print(vector.sequenceNum);
        Serial.print(" | AI Directive: ");
        Serial.println(aiPrompt);
        return true;
    }
};

AnnonSuggestionEngine suggestionEngine;
AnnonAgencyBridge agencyBridge;

// Mesh state tracking
uint32_t localSequenceCounter = 0;
float lastBroadcastBearing = 0.0;
unsigned long lastTransmissionTime = 0;
const unsigned long MIN_TRANSMISSION_INTERVAL_MS = 2500; // Rate limit

void initAnnonTacticalBridge() {
    Serial.println("Annon Tactical Bridge Initialized [Collision Guard Active].");
}

void processIncomingTacticalData(const TacticalVector &incomingVector) {
    String tacticalBrief = suggestionEngine.evaluateTacticalContext(incomingVector);
    
    Serial.print("[SPEECH SYNTHESIZER AUDIO OUT]: \"");
    Serial.print(tacticalBrief);
    Serial.println("\"");
    
    agencyBridge.transmitTelemetryToDispatch(incomingVector, tacticalBrief);
}

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW Init Failed.");
        return;
    }
    
    initAnnonTacticalBridge();
}

void loop() {
    // Simulated live telemetry reading
    float liveBearing = -18.4;
    float liveDistance = 28.5;
    float liveConfidence = 0.91;

    unsigned long currentTime = millis();
    
    // Collision Prevention Check 1: Rate Limiting & Significant Change Threshold
    bool significantChange = abs(liveBearing - lastBroadcastBearing) > 5.0;
    bool timeWindowPassed = (currentTime - lastTransmissionTime) > MIN_TRANSMISSION_INTERVAL_MS;

    if (significantChange || timeWindowPassed) {
        // Collision Prevention Check 2: Randomized Backoff Jitter (Stagger transmissions)
        unsigned long jitterDelay = random(50, 400);
        delay(jitterDelay);

        TacticalVector liveTelemetry;
        liveTelemetry.unitID = 1;
        liveTelemetry.sequenceNum = ++localSequenceCounter;
        liveTelemetry.latitude = 45.6387;
        liveTelemetry.longitude = -122.6614;
        liveTelemetry.bearing = liveBearing;
        liveTelemetry.distance = liveDistance;
        liveTelemetry.confidence = liveConfidence;

        // Process locally & broadcast
        processIncomingTacticalData(liveTelemetry);

        // Update state markers
        lastBroadcastBearing = liveBearing;
        lastTransmissionTime = millis();
    }

    delay(500); // Main loop check frequency
}
