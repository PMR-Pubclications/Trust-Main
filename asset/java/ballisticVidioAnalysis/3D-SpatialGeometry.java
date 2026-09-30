package com.forensic.bpa.spatial;

public record Point3D(double x, double y, double z) {
    public Point3D add(Point3D p) {
        return new Point3D(x + p.x, y + p.y, z + p.z);
    }

    public Point3D subtract(Point3D p) {
        return new Point3D(x - p.x, y - p.y, z - p.z);
    }

    public Point3D multiply(double scalar) {
        return new Point3D(x * scalar, y * scalar, z * scalar);
    }

    public double magnitude() {
        return Math.sqrt(x * x + y * y + z * z);
    }

    public Point3D normalize() {
        double mag = magnitude();
        return mag == 0 ? new Point3D(0, 0, 0) : new Point3D(x / mag, y / mag, z / mag);
    }
}
