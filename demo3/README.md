# Smart File Analyzer Tool 🔍🚀

A powerful, complete Python-based desktop application designed for automated file detection and quality analysis. This tool provides a modern UI to help users validate HTML content, detect password protection in documents, and analyze image quality (blur and crop detection), now with full PDF support.

---

## 🎯 Core Features

### 1. **HTML File Detection**
- **Validation**: Does not rely solely on file extensions.
- **Logic**: Validates both the `.html/.htm` extension and the actual file content.

### 2. **Password Protection Detection**
- **PDF**: Uses `PyPDF2` to accurately detect if a PDF is encrypted.
- **Office Documents**: Uses `msoffcrypto-tool` to check for encryption in Word and Excel files.

### 3. **Image & PDF Blur Detection**
- **Technology**: Powered by OpenCV and `pdf2image`.
- **Method**: Converts images/PDFs to grayscale and applies the Laplacian variance method.
- **PDF Support**: Converts the first 3 pages of a PDF to images and averages the blur score.
- **Customizable**: Includes a configurable threshold (default = 100) adjustable via the UI.

### 4. **Cropped / Improper Document Detection**
- **Technology**: Advanced OpenCV processing.
- **Method**: Uses Canny edge detection and contour analysis to identify missing borders or improper framing.

---

## 🖥️ User Interface (PyQt5)

- **Dark Mode UI**: Professional high-contrast theme.
- **Drag & Drop**: Easily add files by dragging them into the application.
- **PDF Preview**: Instantly view the first page of a PDF in the preview panel.
- **Batch Processing**: Process multiple files simultaneously.

---

## 📦 Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Poppler (Required for PDF Analysis)**:
   This tool uses `pdf2image`, which requires **Poppler** to be installed on your system.
   
   **Windows Setup**:
   1. Download the latest Poppler for Windows from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
   2. Extract the ZIP file (e.g., to `C:\poppler`).
   3. Add the `bin` folder (e.g., `C:\poppler\Library\bin`) to your **System PATH**.
   4. Alternatively, you can specify the `poppler_path` in the code if you don't want to add it to PATH.

---

## 🚀 Usage

1. **Run the application**:
   ```bash
   python main.py
   ```
2. **Add Files**: Use the "Add Files" button or drag and drop files.
3. **Analyze**: Click "Start Analysis".
4. **Export**: Save your results to a CSV report.

---

## 📂 Project Architecture

```text
smart_file_analyzer/
│── main.py                # Main entry point
│── requirements.txt       # Project dependencies
│── detectors/             # Core logic
│   ├── html_detector.py
│   ├── password_detector.py
│   ├── image_analyzer.py  # Handles Image & PDF Blur
│   └── age_validator.py
│── ui/                    # UI components
│── utils/                 # Utilities
└── logs/                  # Storage for reports
```
