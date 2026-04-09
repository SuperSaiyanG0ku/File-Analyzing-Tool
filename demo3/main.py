import sys
import os
from PyQt5.QtWidgets import QApplication
from detectors.html_detector import HTMLDetector
from detectors.password_detector import PasswordDetector
from detectors.image_analyzer import ImageAnalyzer
from utils.file_utils import FileUtils
from ui.main_window import SmartFileAnalyzerUI

def main():
    # Ensure logs folder exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Initialize components
    html_detector = HTMLDetector()
    password_detector = PasswordDetector()
    image_analyzer = ImageAnalyzer(blur_threshold=100)
    file_utils = FileUtils(log_dir='logs')

    # Start the UI
    app = QApplication(sys.argv)
    window = SmartFileAnalyzerUI(
        html_detector, 
        password_detector, 
        image_analyzer, 
        file_utils
    )
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
