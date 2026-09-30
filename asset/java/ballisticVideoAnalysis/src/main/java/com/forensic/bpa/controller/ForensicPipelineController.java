package com.forensic.bpa.controller;

import com.forensic.bpa.report.ReportPackagePublisher;
import com.forensic.bpa.service.BloodSpatterAnalyzer;
import com.forensic.bpa.spatial.Ray3D;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/forensics")
public class ForensicPipelineController {

    private final BloodSpatterAnalyzer analyzer = new BloodSpatterAnalyzer();
    private final ReportPackagePublisher publisher = new ReportPackagePublisher();

    @PostMapping("/process-and-push")
    public ResponseEntity<Map<String, Object>> processAndPushToReport(
            @RequestParam("caseId") String caseId,
            @RequestParam("file") MultipartFile file,
            @RequestParam("reportServiceUrl") String reportServiceUrl
    ) {
        try {
            File tempVideo = File.createTempFile("upload_vid_", ".mp4");
            file.transferTo(tempVideo);

            // Run video processing
            BloodSpatterAnalyzer.ForensicAnalysisResult result = analyzer.analyzeVideo(tempVideo);

            // Mocked ray list placeholder for pipeline demonstration
            List<Ray3D> spatterRays = new ArrayList<>();

            // Push payload to report package endpoint
            boolean success = publisher.pushToReportPackage(
                    caseId,
                    tempVideo,
                    spatterRays,
                    result,
                    reportServiceUrl
            );

            tempVideo.delete();

            if (success) {
                return ResponseEntity.ok(Map.of(
                        "status", "SUCCESS",
                        "caseId", caseId,
                        "message", "Forensic video analysis successfully delivered to report package."
                ));
            } else {
                return ResponseEntity.internalServerError().body(Map.of(
                        "status", "ERROR",
                        "message", "Report package service rejected the payload."
                ));
            }

        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "FAILURE",
                    "error", e.getMessage()
            ));
        }
    }
}
