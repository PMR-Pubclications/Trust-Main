package com.forensic.bpa.model;

public class Vector3D {
    public double x, y, z;

    public Vector3D(double x, double y, double z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public Vector3D normalize() {
        double mag = Math.hypot(Math.hypot(x, y), z);
        return !Double.isFinite(mag) || mag == 0
                ? new Vector3D(0, 0, 0)
                : new Vector3D(x / mag, y / mag, z / mag);
    }
}
