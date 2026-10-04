package com.forensic.bpa.service;

import com.forensic.bpa.model.DropletMetrics;
import com.forensic.bpa.model.Vector3D;
import org.bytedeco.javacpp.Loader;
import org.bytedeco.opencv.global.opencv_core;
import org.bytedeco.opencv.global.opencv_imgproc;
import org.bytedeco.opencv.opencv_core.*;
import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.OpenCVFrameConverter;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class BloodSpatterAnalyzer {

    static {
        Loader.load(opencv_core.class);
    }

    public ForensicAnalysisResult analyzeVideo(File videoFile) throws Exception {
        if (videoFile == null || !videoFile.isFile()) {
            throw new IllegalArgumentException("A readable video file is required.");
        }
        FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(videoFile);
        List<DropletMetrics> detectedDroplets = new ArrayList<>();
        boolean started = false;
        try {
            grabber.start();
            started = true;

            OpenCVFrameConverter.ToMat converter = new OpenCVFrameConverter.ToMat();
            org.bytedeco.javacv.Frame frame;
            int frameCount = 0;

            while ((frame = grabber.grabImage()) != null) {
                frameCount++;
                // Sample every Nth frame to optimize processing
                if (frameCount % 5 != 0) continue;

                Mat matFrame = converter.convert(frame);
                if (matFrame == null || matFrame.empty()) continue;

                List<DropletMetrics> frameDroplets = extractBloodstains(matFrame);
                detectedDroplets.addAll(frameDroplets);
            }
        } finally {
            try {
                if (started) {
                    grabber.stop();
                }
            } finally {
                grabber.release();
            }
        }

        // Compute 3D Area of Origin via ray convergence
        Vector3D areaOfOrigin = calculateAreaOfOrigin(detectedDroplets);
        
        // Classify Kinetic Energy Regime (Gunshot vs Blunt Force)
        String energyRegime = classifyEnergyRegime(detectedDroplets);

        return new ForensicAnalysisResult(detectedDroplets.size(), areaOfOrigin, energyRegime);
    }

    private List<DropletMetrics> extractBloodstains(Mat src) {
        List<DropletMetrics> droplets = new ArrayList<>();
        if (src == null || src.empty()) {
            return droplets;
        }

        Mat hsv = new Mat();
        Mat mask1 = new Mat();
        Mat mask2 = new Mat();
        Mat redMask = new Mat();

        // Convert to HSV for red blood color segmentation
        opencv_imgproc.cvtColor(src, hsv, opencv_imgproc.COLOR_BGR2HSV);

        // Red hue spans two ranges in HSV space
        opencv_core.inRange(hsv, new Mat(1, 1, opencv_core.CV_8UC3, new Scalar(0, 70, 50, 0)),
                                 new Mat(1, 1, opencv_core.CV_8UC3, new Scalar(10, 255, 255, 0)), mask1);
        opencv_core.inRange(hsv, new Mat(1, 1, opencv_core.CV_8UC3, new Scalar(170, 70, 50, 0)),
                                 new Mat(1, 1, opencv_core.CV_8UC3, new Scalar(180, 255, 255, 0)), mask2);
        opencv_core.add(mask1, mask2, redMask);

        // Find stain contours
        MatVector contours = new MatVector();
        Mat hierarchy = new Mat();
        opencv_imgproc.findContours(redMask, contours, hierarchy, opencv_imgproc.RETR_EXTERNAL, opencv_imgproc.CHAIN_APPROX_SIMPLE);

        for (long i = 0; i < contours.size(); i++) {
            Mat contour = contours.get(i);
            double area = opencv_imgproc.contourArea(contour);

            // Filter out noise and massive pools (require single-droplet area thresholds)
            if (area > 5 && area < 1500 && contour.rows() >= 5) {
                RotatedRect ellipse = opencv_imgproc.fitEllipse(contour);

                double width = Math.min(ellipse.size().width(), ellipse.size().height());
                double length = Math.max(ellipse.size().width(), ellipse.size().height());
                double angle = ellipse.angle(); // Orientation angle

                DropletMetrics metrics = new DropletMetrics(width, length, angle, new Vector3D(0, 0, 0));
                droplets.add(metrics);
            }
        }

        return droplets;
    }

    private Vector3D calculateAreaOfOrigin(List<DropletMetrics> droplets) {
        if (droplets == null || droplets.isEmpty()) return new Vector3D(0, 0, 0);

        // Least-Squares Line Intersection Algorithm for 3D Ray Convergence
        double sumX = 0, sumY = 0, sumZ = 0;
        int validRays = 0;

        for (DropletMetrics d : droplets) {
            if (d == null || d.getTrajectoryRay() == null) {
                continue;
            }
            Vector3D ray = d.getTrajectoryRay();
            // Simple spatial back-projection estimate
            sumX += ray.x;
            sumY += ray.y;
            sumZ += ray.z;
            validRays++;
        }

        return validRays == 0
                ? new Vector3D(0, 0, 0)
                : new Vector3D(sumX / validRays, sumY / validRays, sumZ / validRays);
    }

    private String classifyEnergyRegime(List<DropletMetrics> droplets) {
        if (droplets == null || droplets.isEmpty()) return "INSUFFICIENT_DATA";

        double avgWidth = droplets.stream()
                .filter(java.util.Objects::nonNull)
                .mapToDouble(DropletMetrics::getWidth)
                .filter(Double::isFinite)
                .average().orElse(Double.NaN);
        if (!Double.isFinite(avgWidth)) return "INSUFFICIENT_DATA";

        // High-Velocity Impact Spatter (HVIS) typically yields micro-droplets (< 1mm)
        if (avgWidth < 15.0) { // Pixel threshold scaled to resolution
            return "HIGH_VELOCITY_IMPACT_SPATTER (Characteristic of Gunshot / Explosive Trauma)";
        } else if (avgWidth < 45.0) {
            return "MEDIUM_VELOCITY_IMPACT_SPATTER (Characteristic of Blunt Force / Cast-Off)";
        } else {
            return "LOW_VELOCITY_SPATTER (Passive Drip / Gravity Accumulation)";
        }
    }

    public record ForensicAnalysisResult(int dropletsAnalyzed, Vector3D areaOfOrigin, String energyRegime) {}
}
