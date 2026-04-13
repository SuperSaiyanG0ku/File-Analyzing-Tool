DARK_MODE_STYLE = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #181825;
}
QPushButton#analyzeBtn {
    background-color: #89b4fa;
    color: #11111b;
}
QPushButton#analyzeBtn:hover {
    background-color: #b4befe;
}
QListWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #313244;
}
QListWidget::item:selected {
    background-color: #313244;
    color: #89b4fa;
}
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    background-color: #181825;
    height: 12px;
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 6px;
}
QLabel#titleLabel {
    font-size: 28px;
    font-weight: bold;
    color: #89b4fa;
    margin-bottom: 25px;
}
QLabel#statusLabel {
    color: #bac2de;
    font-size: 14px;
}
QScrollArea {
    border: none;
}
QTableWidget {
    background-color: #181825;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 8px;
    font-weight: bold;
}
QSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
}
"""
