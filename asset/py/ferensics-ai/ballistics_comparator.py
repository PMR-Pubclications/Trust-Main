import cv2
import numpy as np
from scipy.signal import correlate
from typing import Dict, Any, Tuple


class BallisticsComparator:
    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # 1. BULLET LAND-AND-GROOVE STRIATION COMPARISON (1D Profile Matching)
    # -------------------------------------------------------------------------
    @staticmethod
    def extract_1d_striation_profile(cropped_lea_image: np.ndarray) -> np.ndarray:
        """
        Extracts a 1D mean depth/intensity profile along bullet land striation lines.
        Expects striations aligned vertically; averages across column axis.
        """
        if len(cropped_lea_image.shape) == 3:
            gray = cv2.cvtColor(cropped_lea_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cropped_lea_image.copy()

        # High-pass filter to remove land curvature and keep fine striations
        gaussian_blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=15)
        detrended = cv2.subtract(gray, gaussian_blur)

        # Average horizontally across striations to produce 1D profile vector
        profile_1d = np.mean(detrended, axis=0)
        
        # Z-score normalization: (x - mean) / std
        std = np.std(profile_1d)
        if std > 0:
            profile_1d = (profile_1d - np.mean(profile_1d)) / std
            
        return profile_1d

    @classmethod
    def compare_bullet_striations(
        cls, 
        image_a: np.ndarray, 
        image_b: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculates Maximum Cross-Correlation Coefficient (CCFr) between two 1D land profiles.
        NIST Standard threshold: CCFr > 0.60 indicates strong match candidate.
        """
        prof_a = cls.extract_1d_striation_profile(image_a)
        prof_b = cls.extract_1d_striation_profile(image_b)

        # Compute full cross-correlation
        ccf = correlate(prof_a, prof_b, mode='full')
        norm = np.sqrt(np.sum(prof_a**2) * np.sum(prof_b**2))
        
        if norm > 0:
            ccf_normalized = ccf / norm
            max_ccf = float(np.max(ccf_normalized))
            best_shift = int(np.argmax(ccf_normalized) - (len(prof_b) - 1))
        else:
            max_ccf = 0.0
            best_shift = 0

        return {
            "ccfr_score": round(max_ccf, 4),
            "alignment_shift_pixels": best_shift,
            "is_match_candidate": max_ccf >= 0.60
        }

    # -------------------------------------------------------------------------
    # 2. FIRING PIN & BREECH FACE IMPRESSION MATCHING (2D Surface Analysis)
    # -------------------------------------------------------------------------
    @staticmethod
    def align_and_compare_firing_pins(
        impression_a: np.ndarray, 
        impression_b: np.ndarray
    ) -> Dict[str, Any]:
        """
        Aligns two firing pin impression images in rotation and translation using 
        Log-Polar transform + Phase Correlation, then returns Structural Similarity (SSIM).
        """
        def to_gray_norm(img):
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.resize(img, (256, 256))

        img1 = to_gray_norm(impression_a)
        img2 = to_gray_norm(impression_b)

        # 1. Log-Polar Transform for Rotational Alignment
        center = (128, 128)
        max_radius = 128
        polar1 = cv2.warpPolar(img1, (256, 256), center, max_radius, cv2.WARP_POLAR_LOG)
        polar2 = cv2.warpPolar(img2, (256, 256), center, max_radius, cv2.WARP_POLAR_LOG)

        # 2. Estimate rotational shift via Phase Correlation
        (d_x, d_y), response = cv2.phaseCorrelate(
            np.float32(polar1), 
            np.float32(polar2)
        )
        
        # Convert y-shift in polar space back to rotation angle in degrees
        rotation_angle = (d_y / 256.0) * 360.0

        # Rotate Image B to align with Image A
        rot_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        img2_aligned = cv2.warpAffine(img2, rot_matrix, (256, 256))

        # 3. Compute Normalized Cross-Correlation (NCC) on aligned images
        res = cv2.matchTemplate(img1, img2_aligned, cv2.TM_CCORR_NORMED)
        ncc_score = float(res[0][0])

        return {
            "rotation_correction_degrees": round(rotation_angle, 2),
            "confidence_response": round(response, 4),
            "ncc_match_score": round(ncc_score, 4),
            "is_match_candidate": ncc_score >= 0.75
        }


# --- DEMO TESTING ---
if __name__ == "__main__":
    comparator = BallisticsComparator()

    # Generate synthetic bullet land profiles (simulated 1D striations)
    x = np.linspace(0, 10, 500)
    striation_signal = np.sin(x*5) + np.sin(x*12) + np.random.normal(0, 0.1, 500)
    
    # Image A & Image B (shifted by 12 pixels with slight noise)
    img_a = np.tile(striation_signal, (100, 1)).astype(np.float32)
    img_b = np.tile(np.roll(striation_signal, 12) + np.random.normal(0, 0.05, 500), (100, 1)).astype(np.float32)

    result = comparator.compare_bullet_striations(img_a, img_b)
    print("\n[BULLET STRIATION MATCH RESULT]:")
    print(f"  CCFr Correlation Score: {result['ccfr_score']}")
    print(f"  Calculated Pixel Shift: {result['alignment_shift_pixels']} px")
    print(f"  Match Verdict:          {result['is_match_candidate']}")
