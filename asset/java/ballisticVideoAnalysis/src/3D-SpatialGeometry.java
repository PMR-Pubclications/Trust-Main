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
        return Math.hypot(Math.hypot(x, y), z);
    }

    public Point3D normalize() {
        double mag = magnitude();
        return !Double.isFinite(mag) || mag == 0
                ? new Point3D(0, 0, 0)
                : new Point3D(x / mag, y / mag, z / mag);
    }
}

package com.forensic.bpa.spatial;

public record Ray3D(Point3D anchor, Point3D direction) {
    public Ray3D {
        anchor = anchor == null ? new Point3D(0, 0, 0) : anchor;
        direction = direction == null ? new Point3D(0, 0, 0) : direction.normalize();
    }
}
