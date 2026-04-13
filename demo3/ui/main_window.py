import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QListWidget, QTableWidget, QTableWidgetItem, 
    QHeaderView, QProgressBar, QSplitter, QScrollArea, QFrame, QMessageBox,
    QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QImage
from .styles import DARK_MODE_STYLE

class AnalysisThread(QThread):
    progress = pyqtSignal(int, dict)
    finished = pyqtSignal(list)

    def __init__(self, files, html_detector, password_detector, image_analyzer, age_validator, file_utils, blur_threshold):
        super().__init__()
        self.files = files
        self.html_detector = html_detector
        self.password_detector = password_detector
        self.image_analyzer = image_analyzer
        self.age_validator = age_validator
        self.file_utils = file_utils
        self.blur_threshold = blur_threshold

    def run(self):
        results = []
        # Update image analyzer threshold before running
        self.image_analyzer.blur_threshold = self.blur_threshold
        
        for i, file_path in enumerate(self.files):
            try:
                file_type = self.file_utils.get_file_type(file_path)
                result = {
                    'File Name': os.path.basename(file_path),
                    'Path': file_path,
                    'Type': file_type,
                    'HTML': 'N/A',
                    'Protected': 'N/A',
                    'Blurry': 'N/A',
                    'Cropped': 'N/A',
                    'File Date': 'N/A',
                    'Age (Days)': 'N/A',
                    'Eligibility': 'N/A',
                    'Final Status': 'Valid',
                    'Reason': ''
                }

                # Validation tracking
                reasons = []

                # File Age Validation
                age_info = self.age_validator.check_file_age(file_path)
                if "error" not in age_info:
                    result['File Date'] = age_info['file_date']
                    result['Age (Days)'] = f"{age_info['age_days']} days"
                    result['Eligibility'] = "✅ Eligible" if age_info['is_eligible'] else "❌ Not Eligible"
                    if not age_info['is_eligible']:
                        reasons.append("Older than 1 year")

                if file_type == 'HTML':
                    is_html = self.html_detector.is_html(file_path)
                    result['HTML'] = 'Yes' if is_html else 'No'
                
                if file_type in ['PDF', 'Word Document', 'Excel Spreadsheet']:
                    is_prot = self.password_detector.is_protected(file_path)
                    result['Protected'] = 'Yes' if is_prot else 'No'

                if file_type in ['Image', 'PDF']:
                    is_blurry, blur_score = self.image_analyzer.analyze_blur(file_path)
                    result['Blurry'] = 'Yes' if is_blurry else 'No'
                    if is_blurry:
                        reasons.append("Blurry")
                    
                    if file_type == 'Image':
                        is_cropped, crop_score = self.image_analyzer.analyze_crop(file_path)
                        result['Cropped'] = 'Yes' if is_cropped else 'No'
                        if is_cropped:
                            reasons.append("Cropped")

                # Final Validation Status
                if reasons:
                    result['Final Status'] = '❌ Not Valid'
                    result['Reason'] = ", ".join(reasons)
                else:
                    result['Final Status'] = '✅ Valid'
                    result['Reason'] = "All checks passed"

                self.file_utils.log_analysis(file_path, result)
                results.append(result)
                self.progress.emit(int((i + 1) / len(self.files) * 100), result)
            except Exception as e:
                results.append({
                    'File Name': os.path.basename(file_path),
                    'Path': file_path,
                    'Status': f'Error: {str(e)}'
                })
        self.finished.emit(results)

class SmartFileAnalyzerUI(QMainWindow):
    def __init__(self, html_detector, password_detector, image_analyzer, age_validator, file_utils):
        super().__init__()
        self.html_detector = html_detector
        self.password_detector = password_detector
        self.image_analyzer = image_analyzer
        self.age_validator = age_validator
        self.file_utils = file_utils
        self.current_files = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart File Analyzer Tool")
        self.resize(1100, 800)
        self.setAcceptDrops(True)
        self.setStyleSheet(DARK_MODE_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Smart File Analyzer Tool")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Settings Group
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QHBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Blur Threshold:"))
        self.blur_spin = QSpinBox()
        self.blur_spin.setRange(10, 1000)
        self.blur_spin.setValue(100)
        self.blur_spin.setFixedWidth(80)
        settings_layout.addWidget(self.blur_spin)
        settings_layout.addStretch()
        main_layout.addWidget(settings_group)

        # Horizontal Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.update_preview)
        left_layout.addWidget(QLabel("📂 Selected Files:"))
        left_layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Files")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_list)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)

        self.btn_analyze = QPushButton("Start Analysis")
        self.btn_analyze.setObjectName("analyzeBtn")
        self.btn_analyze.clicked.connect(self.start_analysis)
        self.btn_analyze.setFixedHeight(45)
        left_layout.addWidget(self.btn_analyze)

        splitter.addWidget(left_panel)

        # Right Panel
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.preview_label = QLabel("Drop files here or use Add button")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(350, 350)
        self.preview_label.setStyleSheet("border: 2px dashed #45475a; border-radius: 12px; background-color: #181825;")
        right_layout.addWidget(self.preview_label)

        self.info_panel = QLabel("Select a file to see details")
        self.info_panel.setStyleSheet("font-size: 14px; color: #bac2de;")
        self.info_panel.setWordWrap(True)
        self.info_panel.setAlignment(Qt.AlignTop)
        right_layout.addWidget(self.info_panel)

        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)

        # Results Table
        self.results_table = QTableWidget(0, 11)
        self.results_table.setHorizontalHeaderLabels([
            "File Name", "Type", "HTML", "Protected", "Blurry", "Cropped", "File Date", "Age (Days)", "Eligibility", "Final Status", "Reason"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        main_layout.addWidget(QLabel("📊 Analysis Results:"))
        main_layout.addWidget(self.results_table)

        # Bottom Bar
        bottom_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)
        
        self.btn_export = QPushButton("Export Results")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        self.btn_export.setFixedWidth(150)
        bottom_layout.addWidget(self.btn_export)
        
        main_layout.addLayout(bottom_layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.add_files_to_list(files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*.*)")
        if files:
            self.add_files_to_list(files)

    def add_files_to_list(self, files):
        for f in files:
            if f not in self.current_files:
                self.current_files.append(f)
                self.file_list.addItem(os.path.basename(f))
        self.update_preview()

    def clear_list(self):
        self.current_files = []
        self.file_list.clear()
        self.results_table.setRowCount(0)
        self.preview_label.clear()
        self.preview_label.setText("Drop files here or use Add button")
        self.btn_export.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

    def update_preview(self):
        selected = self.file_list.currentRow()
        if selected >= 0:
            file_path = self.current_files[selected]
            file_type = self.file_utils.get_file_type(file_path)
            self.info_panel.setText(f"<b>File:</b> {os.path.basename(file_path)}<br><b>Type:</b> {file_type}<br><b>Path:</b> {file_path}")
            
            if file_type == 'Image':
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
            elif file_type == 'PDF':
                # Generate PDF preview
                img_array = self.image_analyzer.get_pdf_preview(file_path)
                if img_array is not None:
                    h, w, c = img_array.shape
                    bytes_per_line = c * w
                    q_img = QImage(img_array.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_img)
                    scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                else:
                    self.preview_label.clear()
                    self.preview_label.setText("PDF Preview Generation Failed\n(Check Poppler installation)")
            else:
                self.preview_label.clear()
                self.preview_label.setText(f"{file_type} Preview Not Available")

    def start_analysis(self):
        if not self.current_files:
            QMessageBox.warning(self, "Warning", "Please add some files first!")
            return

        self.btn_analyze.setEnabled(False)
        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.analysis_results = []

        self.thread = AnalysisThread(
            self.current_files, self.html_detector, self.password_detector, 
            self.image_analyzer, self.age_validator, self.file_utils, self.blur_spin.value()
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_analysis_finished)
        self.thread.start()

    def update_progress(self, val, result):
        self.progress_bar.setValue(val)
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Helper to set table item with alignment
        def set_item(col, text):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, col, item)

        set_item(0, result.get('File Name', ''))
        set_item(1, result.get('Type', ''))
        set_item(2, result.get('HTML', ''))
        set_item(3, result.get('Protected', ''))
        set_item(4, result.get('Blurry', ''))
        set_item(5, result.get('Cropped', ''))
        set_item(6, result.get('File Date', ''))
        set_item(7, result.get('Age (Days)', ''))
        set_item(8, result.get('Eligibility', ''))
        set_item(9, result.get('Final Status', ''))
        set_item(10, result.get('Reason', ''))

    def on_analysis_finished(self, results):
        self.analysis_results = results
        self.btn_analyze.setEnabled(True)
        self.btn_export.setEnabled(True)
        QMessageBox.information(self, "Success", f"Analysis completed for {len(results)} files.")

    def export_results(self):
        if self.analysis_results:
            path = self.file_utils.export_results_to_csv(self.analysis_results)
            QMessageBox.information(self, "Exported", f"Results exported to:\n{path}")
