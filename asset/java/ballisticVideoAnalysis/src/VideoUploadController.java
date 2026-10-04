package com.forensic.bpa.controller;

import com.forensic.bpa.service.BloodSpatterAnalyzer;
import com.forensic.bpa.service.BloodSpatterAnalyzer.ForensicAnalysisResult;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;

@RestController
@RequestMapping("/api/forensics")
public class ForensicVideoController {

    private final BloodSpatterAnalyzer analyzer = new BloodSpatterAnalyzer();

    @PostMapping("/analyze-spatter")
    public ResponseEntity<ForensicAnalysisResult> uploadAndAnalyzeVideo(@RequestParam("file") MultipartFile file) {
        if (file == null || file.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        File tempFile = null;
        try {
            tempFile = File.createTempFile("forensic_vid_", ".mp4");
            file.transferTo(tempFile);

            ForensicAnalysisResult result = analyzer.analyzeVideo(tempFile);
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().build();
        } finally {
            if (tempFile != null) {
                tempFile.delete();
            }
        }
    }
}
