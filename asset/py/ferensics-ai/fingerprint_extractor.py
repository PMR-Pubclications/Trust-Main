import cv2
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple


class FingerprintMinutiaeExtractor:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        
        # PyTorch 3x3 8-neighbor summation kernel
        # Counts surrounding adjacent ridge pixels for every pixel in parallel
        self.neighbor_kernel = torch.tensor([[
            [[1.0, 1.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0]]
        ]], dtype=torch.float32).to(self.device)

    def preprocess_and_thin(self, image_path: str) -> np.ndarray:
        """
        1. Normalizes intensity contrast.
        2. Applies adaptive thresholding for binarization.
        3. Reduces ridges to a 1-pixel skeleton via morphological thinning.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Image not found at: {image_path}")

        # Normalize intensity
        normalized = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        
        # Smooth noise while preserving ridge edges
        blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
        
        # Adaptive Thresholding (Ridges = 1, Background = 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        binary_mask = (binary > 0).astype(np.uint8)

        # Zhang-Suen morphological thinning to produce 1-pixel wide ridges
        try:
            skeleton = cv2.ximgproc.thinning(binary_mask * 255, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN) // 255
        except AttributeError:
            # Fallback thinning using iterative erosion/dilation
            skeleton = self._morphological_thinning_fallback(binary_mask)
            
        return skeleton

    def extract_minutiae(self, skeleton: np.ndarray, margin: int = 15) -> Dict[str, List[Tuple[int, int]]]:
        """
        Extracts Terminations (Endings) and Bifurcations using PyTorch 2D Convolution.
        """
        h, w = skeleton.shape
        tensor_skel = torch.from_numpy(skeleton).float().unsqueeze(0).unsqueeze(0).to(self.device)

        # Convolve 3x3 kernel over skeleton tensor
        neighbor_counts = F.conv2d(tensor_skel, self.neighbor_kernel, padding=1)
        
        # Mask counts so we only check actual ridge pixels (where skeleton == 1)
        masked_counts = neighbor_counts * tensor_skel
        counts_np = masked_counts.squeeze().cpu().numpy()

        # Crossing Number Logic on 1-pixel thinned ridges:
        # Neighbor count == 1 -> Ridge Ending (Termination)
        # Neighbor count == 3 -> Bifurcation
        terminations = np.argwhere(counts_np == 1)
        bifurcations = np.argwhere(counts_np == 3)

        # Filter out boundary artifacts near outer edges
        clean_terminations = [
            (int(y), int(x)) for y, x in terminations 
            if margin <= y <= h - margin and margin <= x <= w - margin
        ]
        clean_bifurcations = [
            (int(y), int(x)) for y, x in bifurcations 
            if margin <= y <= h - margin and margin <= x <= w - margin
        ]

        return {
            "terminations": clean_terminations,
            "bifurcations": clean_bifurcations
        }

    def visualize_and_save(self, skeleton: np.ndarray, minutiae: Dict[str, List[Tuple[int, int]]], output_path: str = "minutiae_output.png"):
        """Draws red circles for terminations and green circles for bifurcations."""
        vis = cv2.cvtColor(skeleton * 255, cv2.COLOR_GRAY2BGR)

        # Red = Ridge Endings (Terminations)
        for y, x in minutiae["terminations"]:
            cv2.circle(vis, (x, y), 3, (0, 0, 255), 1)

        # Green = Bifurcations
        for y, x in minutiae["bifurcations"]:
            cv2.circle(vis, (x, y), 3, (0, 255, 0), 1)

        cv2.imwrite(output_path, vis)
        print(f"[SUCCESS] Processed {len(minutiae['terminations'])} terminations and {len(minutiae['bifurcations'])} bifurcations.")
        print(f"[OUTPUT] Saved image to {output_path}")

    def _morphological_thinning_fallback(self, img: np.ndarray) -> np.ndarray:
        """Standard morphological thinning loop if opencv-contrib is not available."""
        skel = np.zeros(img.shape, np.uint8)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        temp = img.copy()

        while True:
            eroded = cv2.erode(temp, element)
            temp_open = cv2.dilate(eroded, element)
            sub = cv2.subtract(temp, temp_open)
            skel = cv2.bitwise_or(skel, sub)
            temp = eroded.copy()
            if cv2.countNonZero(temp) == 0:
                break
        return skel


if __name__ == "__main__":
    extractor = FingerprintMinutiaeExtractor(device="cpu")
    
    # Process fingerprint image
    # skeleton = extractor.preprocess_and_thin("sample_fingerprint.png")
    # minutiae = extractor.extract_minutiae(skeleton)
    # extractor.visualize_and_save(skeleton, minutiae)
