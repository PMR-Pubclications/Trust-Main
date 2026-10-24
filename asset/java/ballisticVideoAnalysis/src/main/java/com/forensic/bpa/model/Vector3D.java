package com.forensic.bpa.model;

public class Vector3D {
    public double x, y, z;

    public Vector3D(double x, double y, double z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public Vector3D normalize() {
        double mag = Math.sqrt(x * x + y * y + z * z);
        return new Vector3D(x / mag, y / mag, z / mag);
    }
}
