import sys
import os
from PyQt5.QtWidgets import QApplication
from detectors.html_detector import HTMLDetector
from detectors.password_detector import PasswordDetector
from detectors.image_analyzer import ImageAnalyzer
from detectors.age_validator import AgeValidator
from utils.file_utils import FileUtils
from ui.main_window import SmartFileAnalyzerUI

def main():
    # Ensure logs folder exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Initialize components
    html_detector = HTMLDetector()
    password_detector = PasswordDetector()
    # Auto-detect Poppler path for the user
    poppler_path = r"C:\KYC tool\poppler\poppler-24.02.0\Library\bin"
    image_analyzer = ImageAnalyzer(blur_threshold=100, poppler_path=poppler_path)
    age_validator = AgeValidator()
    file_utils = FileUtils(log_dir='logs')

    # Start the UI
    app = QApplication(sys.argv)
    window = SmartFileAnalyzerUI(
        html_detector, 
        password_detector, 
        image_analyzer, 
        age_validator,
        file_utils
    )
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
