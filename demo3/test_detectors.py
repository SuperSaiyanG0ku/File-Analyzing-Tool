import os
from detectors.html_detector import HTMLDetector
from detectors.password_detector import PasswordDetector
from detectors.image_analyzer import ImageAnalyzer
from detectors.age_validator import AgeValidator
from utils.file_utils import FileUtils

def test_detectors():
    print("--- Testing HTML Detector ---")
    html_det = HTMLDetector()
    print(f"Is test.html HTML? {html_det.is_html('test.html')}")
    print(f"Is requirements.txt HTML? {html_det.is_html('requirements.txt')}")

    print("\n--- Testing Password Detector (Mocking) ---")
    pass_det = PasswordDetector()
    print(f"Checking test.html (should be False): {pass_det.is_protected('test.html')}")

    print("\n--- Testing Age Validator ---")
    age_val = AgeValidator()
    age_info = age_val.check_file_age('test.html')
    print(f"test.html Age Info: {age_info}")

    print("\n--- Testing PDF Blur Detection (Mocking if no PDF) ---")
    poppler_path = r"C:\KYC tool\poppler\poppler-24.02.0\Library\bin"
    img_analyzer = ImageAnalyzer(blur_threshold=100, poppler_path=poppler_path)
    
    # Try to find any PDF in the current directory
    pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if pdfs:
        is_blurry, score = img_analyzer.check_pdf_blur(pdfs[0])
        print(f"Testing PDF {pdfs[0]}: Blurry={is_blurry}, Score={score:.2f}")
    else:
        print("No PDF file found in current directory to test.")

    print("\n--- Testing File Utils ---")
    utils = FileUtils()
    print(f"File type of test.html: {utils.get_file_type('test.html')}")
    print(f"File type of main.py: {utils.get_file_type('main.py')}")

if __name__ == "__main__":
    test_detectors()
