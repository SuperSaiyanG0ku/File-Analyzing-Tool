import cv2
import numpy as np
from pdf2image import convert_from_path

class ImageAnalyzer:
    def __init__(self, blur_threshold=100, poppler_path=None):
        self.blur_threshold = blur_threshold
        self.poppler_path = poppler_path

    def analyze_blur(self, file_path):
        """
        Detect if an image or PDF is blurry.
        For PDF, it converts the first 3 pages to images and averages the blur score.
        """
        if file_path.lower().endswith('.pdf'):
            return self.check_pdf_blur(file_path)
            
        try:
            image = cv2.imread(file_path)
            if image is None:
                return False, 0.0
            
            return self._calculate_blur(image)
        except Exception as e:
            print(f"Error analyzing blur: {e}")
            return False, 0.0

    def _calculate_blur(self, image):
        """Helper to calculate blur score for a single CV2 image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = variance < self.blur_threshold
        return is_blurry, variance

    def check_pdf_blur(self, pdf_path):
        """
        Convert first 3 pages of PDF to images and check for blur.
        """
        try:
            # Convert first 3 pages
            images = convert_from_path(
                pdf_path, 
                last_page=3, 
                poppler_path=self.poppler_path,
                fmt='jpeg'
            )
            
            if not images:
                return False, 0.0
                
            scores = []
            for img in images:
                # Convert PIL to CV2
                open_cv_image = np.array(img)
                open_cv_image = open_cv_image[:, :, ::-1].copy() # RGB to BGR
                _, score = self._calculate_blur(open_cv_image)
                scores.append(score)
            
            avg_score = sum(scores) / len(scores)
            is_blurry = avg_score < self.blur_threshold
            return is_blurry, avg_score
            
        except Exception as e:
            print(f"Error checking PDF blur: {e}")
            return False, 0.0

    def get_pdf_preview(self, pdf_path):
        """
        Returns the first page of the PDF as a CV2 image for preview.
        """
        try:
            images = convert_from_path(
                pdf_path, 
                first_page=1, 
                last_page=1, 
                poppler_path=self.poppler_path,
                fmt='jpeg'
            )
            if images:
                open_cv_image = np.array(images[0])
                return open_cv_image # Return as RGB for QPixmap
            return None
        except Exception as e:
            print(f"Error generating PDF preview: {e}")
            return None

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
            box = np.int64(box)
            
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
