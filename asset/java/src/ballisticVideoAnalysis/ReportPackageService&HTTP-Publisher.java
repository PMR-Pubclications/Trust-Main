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
     * Compiles analysis metrics into a report package and pushes it to the target endpoint.
     */
    public boolean pushToReportPackage(
            String caseId,
            File sourceVideo,
            List<Ray3D> spatterRays,
            BloodSpatterAnalyzer.ForensicAnalysisResult analysisResult,
            String reportPackageEndpointUrl
    ) throws Exception {

        // 1. Calculate 3D Spatial Origin and Shooter Line-of-Fire Vector
        Point3D origin = Trajectory3DSolver.computeAreaOfOrigin(spatterRays);
        Ray3D shooterRay = Trajectory3DSolver.extrapolateShooterVector(origin, spatterRays);

        // 2. Export 3D Scene Geometry to Temporary OBJ File
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

        // 3. Convert 3D Direction Vector to Spherical Coordinates (Azimuth & Elevation)
        Point3D dir = shooterRay.direction();
        double azimuth = Math.toDegrees(Math.atan2(dir.x(), dir.y()));
        if (azimuth < 0) azimuth += 360.0;
        
        double horizontalMag = Math.sqrt(dir.x() * dir.x() + dir.y() * dir.y());
        double elevation = Math.toDegrees(Math.atan2(dir.z(), horizontalMag));

        // 4. Construct the Report Package Object
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
                Map.of(
                        "sourceVideoName", sourceVideo.getName(),
                        "videoSizeBytes", sourceVideo.length(),
                        "analyzerEngine", "JavaCV-BPA-3D-v1.2"
                ),
                objBase64
        );

        // 5. Serialize Payload to JSON
        String jsonPayload = mapper.writeValueAsString(reportPackage);

        // 6. Push via HTTP POST to Report Package API
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(reportPackageEndpointUrl))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        return response.statusCode() == 200 || response.statusCode() == 201;
    }
}
