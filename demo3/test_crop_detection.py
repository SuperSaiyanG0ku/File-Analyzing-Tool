import cv2
import numpy as np
import os
from detectors.image_analyzer import ImageAnalyzer

def create_test_image(filename, rect_coords, img_size=(800, 600)):
    """Creates a test image with a white rectangle on a black background."""
    img = np.zeros((img_size[1], img_size[0], 3), dtype=np.uint8)
    x, y, w, h = rect_coords
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)
    cv2.imwrite(filename, img)
    return filename

def test_crop_detection():
    analyzer = ImageAnalyzer()
    
    print("--- Testing Crop Detection with Synthetic Images ---")
    
    # Test Case 1: Centered Document (Not Cropped)
    # 400x300 rect in 800x600 image, centered
    centered_img = create_test_image("test_centered.jpg", (200, 150, 400, 300))
    is_cropped, conf = analyzer.analyze_crop(centered_img)
    print(f"Centered Image: Cropped={is_cropped}, Confidence={conf:.2f} (Expected: False)")
    
    # Test Case 2: Cropped Document (Touching 3 edges)
    # 400x300 rect touching top, left, and right edges
    cropped_img = create_test_image("test_cropped.jpg", (0, 0, 800, 300))
    is_cropped, conf = analyzer.analyze_crop(cropped_img)
    print(f"Cropped Image (3 edges): Cropped={is_cropped}, Confidence={conf:.2f} (Expected: True)")
    
    # Test Case 3: Improper Framing (Touching 1 edge)
    # 400x300 rect touching only the left edge
    improper_img = create_test_image("test_improper.jpg", (0, 150, 400, 300))
    is_cropped, conf = analyzer.analyze_crop(improper_img)
    print(f"Improper Framing (1 edge): Cropped={is_cropped}, Confidence={conf:.2f} (Expected: False or low confidence)")

    # Cleanup
    for f in ["test_centered.jpg", "test_cropped.jpg", "test_improper.jpg"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    test_crop_detection()
