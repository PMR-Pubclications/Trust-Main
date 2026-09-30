package com.forensic.bpa.report;

import com.forensic.bpa.spatial.Point3D;
import com.forensic.bpa.spatial.Ray3D;

import java.time.Instant;
import java.util.Base64;
import java.util.Map;

public record ForensicReportPackage(
        String caseId,
        String timestamp,
        int dropletsAnalyzed,
        String energyRegimeClassification,
        SpatialOriginData areaOfOrigin,
        ShooterTrajectoryData shooterTrajectory,
        Map<String, Object> metadata,
        String objMeshBase64
) {
    public record SpatialOriginData(double xMeters, double yMeters, double zMeters) {}
    
    public record ShooterTrajectoryData(
            double azimuthDegrees,
            double elevationDegrees,
            Vector3DData directionVector
    ) {}
    
    public record Vector3DData(double dx, double dy, double dz) {}
}
