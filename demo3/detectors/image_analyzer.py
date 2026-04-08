import cv2
import numpy as np

class ImageAnalyzer:
    def __init__(self, blur_threshold=100):
        self.blur_threshold = blur_threshold

    def analyze_blur(self, image_path):
        """
        Detect if an image is blurry using Laplacian variance.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, 0.0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            is_blurry = variance < self.blur_threshold
            return is_blurry, variance
        except Exception as e:
            print(f"Error analyzing blur: {e}")
            return False, 0.0

    def analyze_crop(self, image_path):
        """
        Detect if an image is cropped or improperly framed.
        Checks for missing borders, framing, and aspect ratio.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, 0.0
            
            h, w = image.shape[:2]
            aspect_ratio = w / h
            
            # 1. Edge/Contour Detection for Border Missing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Check for edges at the boundary of the image
            # If there are many edges at the boundary, it might be cropped
            boundary_edges = 0
            boundary_edges += np.sum(edges[0, :]) > 0 # top
            boundary_edges += np.sum(edges[-1, :]) > 0 # bottom
            boundary_edges += np.sum(edges[:, 0]) > 0 # left
            boundary_edges += np.sum(edges[:, -1]) > 0 # right
            
            # 2. Contour detection to find the document
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return True, 0.1 # No clear document structure
                
            largest_contour = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(largest_contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            # 3. Framing check (is the main object too close to the edge?)
            x, y, w_rect, h_rect = cv2.boundingRect(largest_contour)
            padding = 10 # pixels
            is_improper_framing = (x < padding or y < padding or 
                                  (x + w_rect) > (w - padding) or 
                                  (y + h_rect) > (h - padding))
            
            # 4. Aspect ratio check (e.g., standard A4 is 1.41)
            # Normal document aspect ratio range: 0.5 to 2.0 (covers most common docs)
            is_abnormal_aspect = aspect_ratio < 0.5 or aspect_ratio > 2.0
            
            # Calculate confidence score (simple heuristic)
            confidence = 0.0
            if boundary_edges >= 3: confidence += 0.4
            if is_improper_framing: confidence += 0.3
            if is_abnormal_aspect: confidence += 0.3
            
            is_cropped = confidence > 0.5
            return is_cropped, confidence
            
        except Exception as e:
            print(f"Error analyzing crop: {e}")
            return False, 0.0
