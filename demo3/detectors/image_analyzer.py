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
        Detect if a document in an image is cropped or improperly framed.
        Uses advanced contour analysis and boundary intersection checks.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, 0.0
            
            h, w = image.shape[:2]
            image_area = h * w
            
            # 1. Preprocessing for better contour detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Use Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Use a combination of thresholding methods
            # Otsu's thresholding often works well for documents on a background
            _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 2. Find contours
            contours, _ = cv2.findContours(thresh_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                # If Otsu fails, try adaptive thresholding
                thresh_adaptive = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                       cv2.THRESH_BINARY, 11, 2)
                contours, _ = cv2.findContours(thresh_adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    return True, 1.0 # No clear document structure detected
            
            # Find the largest contour by area (assuming it's the document)
            document_contour = max(contours, key=cv2.contourArea)
            doc_area = cv2.contourArea(document_contour)
            
            # 3. Check if document is too small (might not be a document)
            if doc_area < (image_area * 0.1):
                return True, 0.8 # Document occupies less than 10% of frame
            
            # 4. Bounding box and boundary intersection check
            # Get the straight bounding box
            x, y, w_doc, h_doc = cv2.boundingRect(document_contour)
            
            # Check for intersection with image boundaries (the primary crop indicator)
            # Padding to account for camera noise or slight rotations
            padding = 10 
            is_touching_left = x <= padding
            is_touching_right = (x + w_doc) >= (w - padding)
            is_touching_top = y <= padding
            is_touching_bottom = (y + h_doc) >= (h - padding)
            
            boundary_touch_count = sum([is_touching_left, is_touching_right, is_touching_top, is_touching_bottom])
            
            # 5. Aspect Ratio check
            aspect_ratio = w_doc / float(h_doc) if h_doc > 0 else 0
            is_abnormal_aspect = aspect_ratio < 0.4 or aspect_ratio > 2.5
            
            # 6. Calculate Confidence Score
            confidence = 0.0
            
            # Touching boundaries is a strong indicator of a crop
            # If 3 or more sides touch, it's definitely cropped
            if boundary_touch_count >= 3:
                confidence = 1.0
            elif boundary_touch_count == 2:
                # Touching 2 parallel sides (top/bottom or left/right) usually means cropped
                if (is_touching_left and is_touching_right) or (is_touching_top and is_touching_bottom):
                    confidence = 0.9
                else:
                    # Touching 2 adjacent sides might just be poor framing
                    confidence = 0.7
            elif boundary_touch_count == 1:
                # Touching 1 side might just be poor framing
                confidence = 0.4
            
            # Adjust confidence based on coverage
            doc_coverage = doc_area / image_area
            if doc_coverage > 0.95:
                # Takes up almost the whole screen, very likely cropped if touching any edge
                if boundary_touch_count >= 1:
                    confidence = max(confidence, 0.8)
            
            if is_abnormal_aspect: 
                confidence = min(confidence + 0.2, 1.0)
            
            # Threshold for declaring "Cropped"
            is_cropped = confidence >= 0.7
            
            return is_cropped, confidence
            
        except Exception as e:
            print(f"Error analyzing crop: {e}")
            return False, 0.0
