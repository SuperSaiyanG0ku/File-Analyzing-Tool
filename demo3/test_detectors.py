import os
from detectors.html_detector import HTMLDetector
from detectors.password_detector import PasswordDetector
from detectors.image_analyzer import ImageAnalyzer
from utils.file_utils import FileUtils

def test_detectors():
    print("--- Testing HTML Detector ---")
    html_det = HTMLDetector()
    print(f"Is test.html HTML? {html_det.is_html('test.html')}")
    print(f"Is requirements.txt HTML? {html_det.is_html('requirements.txt')}")

    print("\n--- Testing Password Detector (Mocking) ---")
    pass_det = PasswordDetector()
    # Since we don't have encrypted files, just verify it runs
    print(f"Checking non-existent file: {pass_det.is_protected('dummy.pdf')}")

    print("\n--- Testing File Utils ---")
    utils = FileUtils()
    print(f"File type of test.html: {utils.get_file_type('test.html')}")
    print(f"File type of main.py: {utils.get_file_type('main.py')}")

if __name__ == "__main__":
    test_detectors()
