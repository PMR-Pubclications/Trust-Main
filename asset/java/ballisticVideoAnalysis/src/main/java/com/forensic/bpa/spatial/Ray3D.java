package com.forensic.bpa.spatial;

public record Ray3D(Point3D anchor, Point3D direction) {
    public Ray3D {
        direction = direction.normalize();
    }
}
