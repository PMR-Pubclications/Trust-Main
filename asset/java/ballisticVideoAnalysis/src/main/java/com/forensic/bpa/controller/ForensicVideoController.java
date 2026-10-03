package com.forensic.bpa.controller;

import com.forensic.bpa.service.BloodSpatterAnalyzer;
import com.forensic.bpa.service.BloodSpatterAnalyzer.ForensicAnalysisResult;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Files;

@RestController
@RequestMapping("/api/forensics")
public class ForensicVideoController {

    private final BloodSpatterAnalyzer analyzer;

    public ForensicVideoController(BloodSpatterAnalyzer analyzer) {
        this.analyzer = analyzer;
    }

    @PostMapping("/analyze-spatter")
    public ResponseEntity<ForensicAnalysisResult> uploadAndAnalyzeVideo(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        File tempFile = null;
        try {
            tempFile = File.createTempFile("forensic_vid_", ".mp4");
            file.transferTo(tempFile);

            ForensicAnalysisResult result = analyzer.analyzeVideo(tempFile);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        } finally {
            if (tempFile != null) {
                try {
                    Files.deleteIfExists(tempFile.toPath());
                } catch (Exception ignored) {
                }
            }
        }
    }
}
