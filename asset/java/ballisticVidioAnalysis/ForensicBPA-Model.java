package com.forensic.bpa.model;

public class DropletMetrics {
    private final double width;
    private final double length;
    private final double orientationDegrees;
    private final double impactAngleRad;
    private final Vector3D trajectoryRay;

    public DropletMetrics(double width, double length, double orientationDegrees, Vector3D cameraPos) {
        this.width = width;
        this.length = Math.max(length, width + 1e-5); // Prevent division by zero
        this.orientationDegrees = orientationDegrees;
        
        // Impact Angle alpha = arcsin(W / L)
        double ratio = Math.min(1.0, this.width / this.length);
        this.impactAngleRad = Math.asin(ratio);
        
        // Calculate 3D unit direction ray pointing back along the line of flight
        double gammaRad = Math.toRadians(orientationDegrees);
        double dx = Math.cos(gammaRad) * Math.cos(this.impactAngleRad);
        double dy = Math.sin(gammaRad) * Math.cos(this.impactAngleRad);
        double dz = -Math.sin(this.impactAngleRad);
        
        this.trajectoryRay = new Vector3D(dx, dy, dz).normalize();
    }

    public double getImpactAngleDegrees() {
        return Math.toDegrees(impactAngleRad);
    }

    public double getWidth() { return width; }
    public double getLength() { return length; }
    public Vector3D getTrajectoryRay() { return trajectoryRay; }
}
