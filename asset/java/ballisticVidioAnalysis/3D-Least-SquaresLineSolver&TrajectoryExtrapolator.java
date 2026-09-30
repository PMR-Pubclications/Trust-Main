package com.forensic.bpa.spatial;

import java.util.List;

public class Trajectory3DSolver {

    /**
     * Solves p0 = (Sum(I - d_i * d_i^T))^-1 * Sum((I - d_i * d_i^T) * a_i)
     */
    public static Point3D computeAreaOfOrigin(List<Ray3D> rays) {
        if (rays == null || rays.isEmpty()) {
            return new Point3D(0, 0, 0);
        }

        double[][] sumMatrix = new double[3][3];
        double[] sumVector = new double[3];

        for (Ray3D ray : rays) {
            Point3D a = ray.anchor();
            Point3D d = ray.direction();

            // Projector Matrix P = I - d * d^T
            double[][] P = new double[][]{
                {1 - d.x() * d.x(), -d.x() * d.y(), -d.x() * d.z()},
                {-d.y() * d.x(), 1 - d.y() * d.y(), -d.y() * d.z()},
                {-d.z() * d.x(), -d.z() * d.y(), 1 - d.z() * d.z()}
            };

            for (int r = 0; r < 3; r++) {
                for (int c = 0; c < 3; c++) {
                    sumMatrix[r][c] += P[r][c];
                }
                sumVector[r] += P[r][0] * a.x() + P[r][1] * a.y() + P[r][2] * a.z();
            }
        }

        return invert3x3AndMultiply(sumMatrix, sumVector);
    }

    /**
     * Projects shooter trajectory line backward from impact point along mean vector.
     */
    public static Ray3D extrapolateShooterVector(Point3D areaOfOrigin, List<Ray3D> rays) {
        double avgDx = 0, avgDy = 0, avgDz = 0;
        for (Ray3D r : rays) {
            avgDx += r.direction().x();
            avgDy += r.direction().y();
            avgDz += r.direction().z();
        }
        int count = rays.size();
        Point3D meanImpactDir = new Point3D(avgDx / count, avgDy / count, avgDz / count).normalize();

        // Reverse direction to vector back to shooter location
        Point3D shooterDirection = meanImpactDir.multiply(-1.0);

        return new Ray3D(areaOfOrigin, shooterDirection);
    }

    private static Point3D invert3x3AndMultiply(double[][] M, double[] V) {
        double det = M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                   - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]);

        if (Math.abs(det) < 1e-9) {
            return new Point3D(0, 0, 0); // Singular matrix fallback
        }

        double invDet = 1.0 / det;

        double[][] inv = new double[3][3];
        inv[0][0] = (M[1][1] * M[2][2] - M[1][2] * M[2][1]) * invDet;
        inv[0][1] = (M[0][2] * M[2][1] - M[0][1] * M[2][2]) * invDet;
        inv[0][2] = (M[0][1] * M[1][2] - M[0][2] * M[1][1]) * invDet;

        inv[1][0] = (M[1][2] * M[2][0] - M[1][0] * M[2][2]) * invDet;
        inv[1][1] = (M[0][0] * M[2][2] - M[0][2] * M[2][0]) * invDet;
        inv[1][2] = (M[0][2] * M[1][0] - M[0][0] * M[1][2]) * invDet;

        inv[2][0] = (M[1][0] * M[2][1] - M[1][1] * M[2][0]) * invDet;
        inv[2][1] = (M[0][1] * M[2][0] - M[0][0] * M[2][1]) * invDet;
        inv[2][2] = (M[0][0] * M[1][1] - M[0][1] * M[1][0]) * invDet;

        double x = inv[0][0] * V[0] + inv[0][1] * V[1] + inv[0][2] * V[2];
        double y = inv[1][0] * V[0] + inv[1][1] * V[1] + inv[1][2] * V[2];
        double z = inv[2][0] * V[0] + inv[2][1] * V[1] + inv[2][2] * V[2];

        return new Point3D(x, y, z);
    }
}
