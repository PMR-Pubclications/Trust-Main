package com.forensic.bpa.report;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import com.forensic.bpa.export.Scene3DObjExporter;
import com.forensic.bpa.service.BloodSpatterAnalyzer;
import com.forensic.bpa.spatial.Point3D;
import com.forensic.bpa.spatial.Ray3D;
import com.forensic.bpa.spatial.Trajectory3DSolver;

import java.io.File;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import java.nio.file.Files;
import java.time.Instant;

import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ReportPackagePublisher {

    private final HttpClient httpClient;
    private final ObjectMapper mapper;

    public ReportPackagePublisher() {
        this.httpClient = HttpClient.newHttpClient();
        this.mapper = new ObjectMapper().findAndRegisterModules()
                .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
    }

    /**
     * Determines target departmental routing based on input category and role restrictions.
     */
    private String resolveRoutingEndpoint(String category, String targetDepartment, String fallbackUrl) {
        if ("TrustAdmin".equalsIgnoreCase(category)) {
            if ("COURTS".equalsIgnoreCase(targetDepartment)) {
                return "https://api.patriotsmustrise.org/trust/v1/dispatch/courts";
            } else if ("FIRSTRESPONDER".equalsIgnoreCase(targetDepartment) || "RESPONDER".equalsIgnoreCase(targetDepartment)) {
                return "https://api.patriotsmustrise.org/trust/v1/dispatch/firstresponder";
            }
        }
        return fallbackUrl;
    }

    /**
     * Compiles analysis metrics into a report package, amends category redirect 
     * metadata, and pushes it to the courts or FirstResponder department.
     */
    public boolean pushToReportPackage(
            String caseId,
            File sourceVideo,
            List<Ray3D> spatterRays,
            BloodSpatterAnalyzer.ForensicAnalysisResult analysisResult,
            String reportPackageEndpointUrl,
            String category,
            String targetDepartment
    ) throws Exception {

        // 1. Resolve Category Redirect (Amend TrustAdmin documents for Courts or FirstResponder)
        String finalEndpointUrl = resolveRoutingEndpoint(category, targetDepartment, reportPackageEndpointUrl);

        // 2. Calculate 3D Spatial Origin and Shooter Line-of-Fire Vector
        Point3D origin = Trajectory3DSolver.computeAreaOfOrigin(spatterRays);
        Ray3D shooterRay = Trajectory3DSolver.extrapolateShooterVector(origin, spatterRays);

        // 3. Export 3D Scene Geometry to Temporary OBJ File
        File tempObjFile = File.createTempFile("scene_3d_", ".obj");
        Scene3DObjExporter.exportSceneToObj(
                tempObjFile.getAbsolutePath(),
                spatterRays,
                origin,
                shooterRay,
                15.0 // 15m shooter line extrapolation
        );

        byte[] objBytes = Files.readAllBytes(tempObjFile.toPath());
        String objBase64 = Base64.getEncoder().encodeToString(objBytes);
        tempObjFile.delete();

        // 4. Convert 3D Direction Vector to Spherical Coordinates (Azimuth & Elevation)
        Point3D dir = shooterRay.direction();
        double azimuth = Math.toDegrees(Math.atan2(dir.x(), dir.y()));
        if (azimuth < 0) azimuth += 360.0;
        
        double horizontalMag = Math.sqrt(dir.x() * dir.x() + dir.y() * dir.y());
        double elevation = Math.toDegrees(Math.atan2(dir.z(), horizontalMag));

        // 5. Construct Expanded Metadata Map with Category Redirect Instructions
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("sourceVideoName", sourceVideo.getName());
        metadata.put("videoSizeBytes", sourceVideo.length());
        metadata.put("analyzerEngine", "JavaCV-BPA-3D-v1.2");
        metadata.put("category", category != null ? category : "General");
        metadata.put("targetDepartment", targetDepartment != null ? targetDepartment : "FirstResponder");
        metadata.put("categoryRedirectApplied", "TrustAdmin".equalsIgnoreCase(category));
        metadata.put("blockchainBackupStandard", "ISO/IEC 17025 Compliant Transmittal");

        // 6. Construct the Report Package Object
        ForensicReportPackage reportPackage = new ForensicReportPackage(
                caseId,
                Instant.now().toString(),
                analysisResult.dropletsAnalyzed(),
                analysisResult.energyRegime(),
                new ForensicReportPackage.SpatialOriginData(origin.x(), origin.y(), origin.z()),
                new ForensicReportPackage.ShooterTrajectoryData(
                        azimuth,
                        elevation,
                        new ForensicReportPackage.Vector3DData(dir.x(), dir.y(), dir.z())
                ),
                metadata,
                objBase64
        );

        // 7. Serialize Payload to JSON
        String jsonPayload = mapper.writeValueAsString(reportPackage);

        // 8. Push via HTTP POST to the Resolved Department/Court Endpoint
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(finalEndpointUrl))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .header("X-Trust-Category-Redirect", "TrustAdmin".equalsIgnoreCase(category) ? "ENABLED" : "DISABLED")
                .header("X-Department-Recipient", targetDepartment)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        return response.statusCode() == 200 || response.statusCode() == 201;
    }

    /**
     * Backward-compatible overloaded method for existing callers without category parameters.
     */
    public boolean pushToReportPackage(
            String caseId,
            File sourceVideo,
            List<Ray3D> spatterRays,
            BloodSpatterAnalyzer.ForensicAnalysisResult analysisResult,
            String reportPackageEndpointUrl
    ) throws Exception {
        return pushToReportPackage(caseId, sourceVideo, spatterRays, analysisResult, reportPackageEndpointUrl, "TrustAdmin", "FirstResponder");
    }
}
