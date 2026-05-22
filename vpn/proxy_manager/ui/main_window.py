import os
import sys
import qtawesome as qta
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QFrame, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QComboBox, QFormLayout, QFileDialog,
                             QMessageBox, QSystemTrayIcon, QMenu, QAction,
                             QGraphicsDropShadowEffect, QSizeGrip)
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QColor, QCursor

from core.proxy_tester import ProxyTester, get_current_ip_info

class MainWindow(QMainWindow):
    def __init__(self, proxy_handler):
        super().__init__()
        self.proxy_handler = proxy_handler
        self.setWindowTitle("Proxy Manager")
        self.resize(1280, 800)
        
        # Frameless Window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.active_proxy = None
        self.selected_proxy = None
        self.dragPos = QPoint()
        
        self.setup_ui()
        self.load_styles()
        self.setup_tray()
        
        # IP Info Update Timer
        self.ip_timer = QTimer()
        self.ip_timer.timeout.connect(self.update_current_info)
        self.ip_timer.start(30000)
        self.update_current_info()

    def setup_ui(self):
        # Central Widget Container (for rounded corners)
        self.container = QWidget()
        self.container.setObjectName("centralWidget")
        self.setCentralWidget(self.container)
        
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.setup_title_bar()

        # 2. Body (Sidebar + Content + Status)
        self.body = QWidget()
        self.body_layout = QHBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        
        self.setup_sidebar()
        
        self.content_stack = QStackedWidget()
        self.body_layout.addWidget(self.content_stack)
        
        self.setup_status_panel()
        
        self.main_layout.addWidget(self.body)
        
        # Size Grip (for resizing frameless window)
        self.sizegrip = QSizeGrip(self.container)
        self.sizegrip.setFixedSize(16, 16)
        
        self.init_views()

    def setup_title_bar(self):
        self.title_bar = QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        layout = QHBoxLayout(self.title_bar)
        layout.setContentsMargins(15, 0, 10, 0)

        # Icon and Title
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.shield-alt', color='#7C3AED').pixmap(QSize(16, 16)))
        layout.addWidget(icon_label)
        
        title = QLabel("PROXY MANAGER")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        layout.addStretch()

        # Control Buttons
        btns = [
            ('fa5s.minus', self.showMinimized, '#64748B'),
            ('fa5s.times', self.close, '#EF4444')
        ]
        for icon, slot, color in btns:
            btn = QPushButton()
            btn.setIcon(qta.icon(icon, color=color))
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 15px; } QPushButton:hover { background: #F1F5F9; }")
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        self.main_layout.addWidget(self.title_bar)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 20, 0, 20)

        # Logo Section
        logo_container = QWidget()
        logo_lay = QHBoxLayout(logo_container)
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon('fa5s.shield-alt', color='#4F46E5').pixmap(QSize(24, 24)))
        logo_lay.addWidget(logo_icon)
        logo_text = QLabel("Proxy Manager")
        logo_text.setStyleSheet("font-size: 18px; font-weight: 700; color: #1E293B;")
        logo_lay.addWidget(logo_text)
        logo_lay.addStretch()
        layout.addWidget(logo_container)
        layout.addSpacing(20)

        # Nav Items
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard", "fa5s.th-large"),
            ("Proxies", "proxies", "fa5s.list"),
            ("Add Proxy", "add_proxy", "fa5s.plus-circle"),
            ("Import/Export", "import_export", "fa5s.file-import"),
            ("Speed Test", "speed_test", "fa5s.tachometer-alt"),
            ("Settings", "settings", "fa5s.cog"),
            ("About", "about", "fa5s.info-circle")
        ]

        for text, key, icon in nav_items:
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color='#94A3B8'))
            btn.setIconSize(QSize(18, 18))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self.switch_view(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()
        self.body_layout.addWidget(self.sidebar)

    def setup_status_panel(self):
        self.status_panel = QFrame()
        self.status_panel.setObjectName("sidebar") # Reuse sidebar bg for right panel
        self.status_panel.setFixedWidth(300)
        layout = QVBoxLayout(self.status_panel)
        layout.setContentsMargins(25, 30, 25, 30)
        layout.setSpacing(20)

        # Connection Card
        self.conn_card = QFrame() # Made it an instance variable
        self.conn_card.setObjectName("card")
        self.conn_card.setStyleSheet("QFrame#card { background-color: #F8FAFC; border: 1px solid #E2E8F0; }")
        card_layout = QVBoxLayout(self.conn_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        self.conn_status_label = QLabel("DISCONNECTED")
        self.conn_status_label.setObjectName("statusOffline")
        self.conn_status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.conn_status_label)

        self.conn_ip_label = QLabel("---.---.---.---")
        self.conn_ip_label.setAlignment(Qt.AlignCenter)
        self.conn_ip_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #1E293B; margin: 10px 0;")
        card_layout.addWidget(self.conn_ip_label)

        self.conn_country_label = QLabel("Unknown Location")
        self.conn_country_label.setAlignment(Qt.AlignCenter)
        self.conn_country_label.setStyleSheet("color: #64748B;")
        card_layout.addWidget(self.conn_country_label)

        self.main_conn_btn = QPushButton("Connect")
        self.main_conn_btn.setObjectName("connectButton") # Changed to use Connect pastel style
        self.main_conn_btn.setFixedHeight(45)
        self.main_conn_btn.clicked.connect(self.toggle_connection)
        card_layout.addWidget(self.main_conn_btn)

        layout.addWidget(self.conn_card)

        # Metrics Section
        metrics_title = QLabel("Connection Metrics")
        metrics_title.setStyleSheet("font-weight: 700; color: #94A3B8; font-size: 11px; text-transform: uppercase;")
        layout.addWidget(metrics_title)

        metrics = [
            ("Ping", "ping_val", "fa5s.bolt", "#FCD34D"),
            ("Uptime", "uptime_val", "fa5s.clock", "#93C5FD"),
            ("Download", "down_val", "fa5s.arrow-down", "#BBF7D0"),
            ("Upload", "up_val", "fa5s.arrow-up", "#FBCFE8")
        ]
        
        for label, attr, icon, color in metrics:
            row = QWidget()
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(0, 0, 0, 0)
            
            icon_l = QLabel()
            icon_l.setPixmap(qta.icon(icon, color=color).pixmap(QSize(14, 14)))
            row_lay.addWidget(icon_l)
            
            txt = QLabel(label)
            txt.setStyleSheet("color: #64748B; font-size: 13px;")
            row_lay.addWidget(txt)
            row_lay.addStretch()
            
            val = QLabel("---")
            val.setStyleSheet("color: #1E293B; font-weight: 600;")
            setattr(self, attr, val)
            row_lay.addWidget(val)
            layout.addWidget(row)

        layout.addStretch()
        self.body_layout.addWidget(self.status_panel)

    def init_views(self):
        self.views = {
            "dashboard": self.create_dashboard_view(),
            "proxies": self.create_proxies_view(),
            "add_proxy": self.create_add_proxy_view(),
            "import_export": self.create_import_export_view(),
            "speed_test": self.create_placeholder_view("Speed Test"),
            "settings": self.create_placeholder_view("Settings"),
            "about": self.create_placeholder_view("About Proxy Manager")
        }
        for view in self.views.values():
            self.content_stack.addWidget(view)
        self.switch_view("dashboard")

    def create_dashboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header
        header = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #1E293B;")
        subtitle = QLabel("Manage your proxy connections simply and securely.")
        subtitle.setStyleSheet("color: #64748B; font-size: 14px;")
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stat_cards_info = [
            ("Total Proxies", "0", "fa5s.list-ul", "total", "#C4B5FD"),
            ("Online", "0", "fa5s.check-circle", "online", "#BBF7D0"),
            ("Active Connection", "None", "fa5s.link", "active", "#BFDBFE")
        ]
        
        self.stat_labels = {}
        for label, val, icon, s_type, color in self.stat_cards_info:
            card = QFrame()
            card.setObjectName("statCard")
            card.setProperty("type", s_type)
            card.setFixedHeight(120)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(20, 20, 20, 20)
            
            top = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 600;")
            top.addWidget(l)
            top.addStretch()
            i = QLabel()
            i.setPixmap(qta.icon(icon, color=color).pixmap(QSize(20, 20)))
            top.addWidget(i)
            c_lay.addLayout(top)
            
            v = QLabel(val)
            v.setStyleSheet("font-size: 24px; font-weight: 700; color: #1E293B;")
            self.stat_labels[label] = v
            c_lay.addWidget(v)
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)

        # Quick Actions
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1E293B;")
        layout.addWidget(actions_title)
        
        actions_lay = QHBoxLayout()
        actions = [
            ("Speed Test", "fa5s.tachometer-alt", "#C4B5FD"),
            ("Check IP", "fa5s.search-location", "#BFDBFE"),
            ("Auto Rotate", "fa5s.sync", "#BBF7D0"),
            ("System Proxy", "fa5s.desktop", "#FBCFE8")
        ]
        for text, icon, color in actions:
            btn = QFrame()
            btn.setObjectName("actionCard")
            btn.setFixedHeight(80)
            b_lay = QHBoxLayout(btn)
            i = QLabel()
            i.setPixmap(qta.icon(icon, color=color).pixmap(QSize(24, 24)))
            b_lay.addWidget(i)
            t = QLabel(text)
            t.setStyleSheet("font-weight: 600; color: #1E293B;")
            b_lay.addWidget(t)
            b_lay.addStretch()
            actions_lay.addWidget(btn)
        layout.addLayout(actions_lay)

        layout.addStretch()
        return view

    def create_proxies_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)
        
        header = QHBoxLayout()
        title = QLabel("Proxies")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search proxies...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.textChanged.connect(self.refresh_proxy_table)
        header.addWidget(self.search_bar)
        
        layout.addLayout(header)

        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(7)
        self.proxy_table.setHorizontalHeaderLabels(["Action", "Country", "IP", "Port", "Type", "Status", "Ping"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proxy_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.proxy_table.itemClicked.connect(self.on_row_clicked)
        layout.addWidget(self.proxy_table)

        self.refresh_proxy_table()
        return view

    def create_add_proxy_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Add Proxy")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        form = QFormLayout(card)
        form.setContentsMargins(30, 30, 30, 30)
        form.setSpacing(15)

        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        self.country_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["HTTP", "HTTPS", "SOCKS5"])
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)

        for label, widget in [("IP Address", self.ip_input), ("Port", self.port_input), 
                             ("Country", self.country_input), ("Type", self.type_input),
                             ("User", self.user_input), ("Pass", self.pass_input)]:
            l = QLabel(label)
            l.setStyleSheet("color: #64748B;")
            form.addRow(l, widget)

        save_btn = QPushButton("Save Proxy")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_proxy)
        form.addRow("", save_btn)

        layout.addWidget(card)
        layout.addStretch()
        return view

    def create_import_export_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Import / Export")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(30, 30, 30, 30)
        c_lay.setSpacing(15)

        import_btn = QPushButton(" Import TXT/CSV")
        import_btn.setIcon(qta.icon('fa5s.file-import', color='white'))
        import_btn.setObjectName("primaryButton")
        import_btn.clicked.connect(self.import_proxies)
        c_lay.addWidget(import_btn)

        export_btn = QPushButton(" Export all to TXT")
        export_btn.setIcon(qta.icon('fa5s.file-export', color='white'))
        export_btn.setStyleSheet("background-color: #1F2937; color: white; border-radius: 10px; padding: 12px;")
        export_btn.clicked.connect(self.export_proxies)
        c_lay.addWidget(export_btn)

        layout.addWidget(card)
        layout.addStretch()
        return view

    def create_placeholder_view(self, text):
        view = QWidget()
        l = QVBoxLayout(view)
        l.setAlignment(Qt.AlignCenter)
        l.addWidget(QLabel(text))
        return view

    # Events for Frameless Window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def toggle_connection(self):
        if self.active_proxy:
            self.disconnect_proxy()
        elif self.selected_proxy:
            # Connect to the currently selected proxy
            row = -1
            # Find the row of the selected proxy to update the button if needed
            for r in range(self.proxy_table.rowCount()):
                item = self.proxy_table.item(r, 1)
                if item and item.data(Qt.UserRole) == self.selected_proxy:
                    row = r
                    break
            self.connect_to_proxy(row, self.selected_proxy)
        else:
            QMessageBox.information(self, "Tip", "Select a proxy from the 'Proxies' tab to connect.")
            self.switch_view("proxies")

    def on_row_clicked(self, item):
        row = item.row()
        # Retrieve the proxy data from column 1
        country_item = self.proxy_table.item(row, 1)
        if country_item:
            p_data = country_item.data(Qt.UserRole)
            self.selected_proxy = p_data
            
            # Update the right status panel with the selected proxy's info
            # but only if we're not currently connected to something else
            if not self.active_proxy:
                self.conn_ip_label.setText(p_data[2])
                self.conn_country_label.setText(p_data[1])
                self.conn_status_label.setText("READY")
                self.conn_status_label.setObjectName("statusReady") # Use pastel Ready style
                self.conn_status_label.style().unpolish(self.conn_status_label)
                self.conn_status_label.style().polish(self.conn_status_label)
                
                # Visual highlight for the connection card
                self.conn_card.setProperty("selected", True)
                self.conn_card.style().unpolish(self.conn_card)
                self.conn_card.style().polish(self.conn_card)

    def switch_view(self, key):
        self.content_stack.setCurrentWidget(self.views[key])
        for k, btn in self.nav_buttons.items():
            active = k == key
            btn.setChecked(active)
            btn.setProperty("active", "true" if active else "false")
            # Avoid using btn.icon().name() which is failing
            icon_map = {
                "dashboard": "fa5s.th-large",
                "proxies": "fa5s.list",
                "add_proxy": "fa5s.plus-circle",
                "import_export": "fa5s.file-import",
                "speed_test": "fa5s.tachometer-alt",
                "settings": "fa5s.cog",
                "about": "fa5s.info-circle"
            }
            icon_name = icon_map.get(k, "fa5s.circle")
            btn.setIcon(qta.icon(icon_name, color='#FFFFFF' if active else '#94A3B8'))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def load_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), "..", "styles", "main.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def refresh_proxy_table(self):
        search = self.search_bar.text()
        proxies = self.proxy_handler.db.search_proxies(search) if search else self.proxy_handler.get_proxies()

        self.proxy_table.setRowCount(0)
        self.stat_labels["Total Proxies"].setText(str(len(proxies)))
        
        if not proxies:
            # Handle empty state (optional improvement)
            pass

        for p in proxies:
            row = self.proxy_table.rowCount()
            self.proxy_table.insertRow(row)
            
            # Action (Column 0)
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            
            conn_btn = QPushButton("Connect")
            conn_btn.setObjectName("connectButton")
            conn_btn.clicked.connect(lambda _, r=row, p_data=p: self.connect_to_proxy(r, p_data))
            
            btn_layout.addWidget(conn_btn)
            self.proxy_table.setCellWidget(row, 0, btn_container)

            # Data (Columns 1-6)
            country_item = QTableWidgetItem(p[1])
            country_item.setData(Qt.UserRole, p) # Store the whole tuple in the first data item
            self.proxy_table.setItem(row, 1, country_item) 
            self.proxy_table.setItem(row, 2, QTableWidgetItem(p[2])) # IP
            self.proxy_table.setItem(row, 3, QTableWidgetItem(p[3])) # Port
            self.proxy_table.setItem(row, 4, QTableWidgetItem(p[6])) # Type
            
            status_item = QTableWidgetItem("Testing...")
            self.proxy_table.setItem(row, 5, status_item) # Status
            self.proxy_table.setItem(row, 6, QTableWidgetItem("...")) # Ping

            self.test_proxy(row, p)

    def test_proxy(self, row, p_data):
        data = {"id": p_data[0], "ip": p_data[2], "port": p_data[3], "proxy_type": p_data[6], "username": p_data[4], "password": p_data[5]}
        tester = ProxyTester(data)
        tester.finished.connect(lambda res: self.update_proxy_status(row, res))
        tester.start()
        if not hasattr(self, 'testers'): self.testers = []
        self.testers.append(tester)

    def update_proxy_status(self, row, result):
        if row < self.proxy_table.rowCount():
            status_item = self.proxy_table.item(row, 5) # Status is now column 5
            ping_item = self.proxy_table.item(row, 6)   # Ping is now column 6
            if status_item:
                status_item.setText(result["status"])
                status_item.setForeground(QColor("#22C55E" if result["status"] == "Online" else "#EF4444"))
            if ping_item:
                ping_item.setText(result["ping"])

    def connect_to_proxy(self, row, p_data):
        if self.active_proxy:
            self.proxy_handler.disconnect_proxy()
        
        if self.proxy_handler.connect_proxy(p_data[2], p_data[3]):
            self.active_proxy = p_data
            self.conn_status_label.setText("CONNECTED")
            self.conn_status_label.setObjectName("statusOnline")
            self.conn_ip_label.setText(p_data[2])
            self.conn_country_label.setText(p_data[1])
            self.main_conn_btn.setText("Disconnect")
            self.main_conn_btn.setStyleSheet("background-color: #EF4444;")
            self.stat_labels["Active Connection"].setText(p_data[2])
            self.update_current_info()
            self.show_notification("Connected", f"Using proxy: {p_data[2]}")
        else:
            QMessageBox.critical(self, "Error", "Failed to connect!")

    def disconnect_proxy(self):
        self.proxy_handler.disconnect_proxy()
        self.active_proxy = None
        self.conn_status_label.setText("DISCONNECTED")
        self.conn_status_label.setObjectName("statusOffline")
        self.conn_ip_label.setText("---.---.---.---")
        self.conn_country_label.setText("Unknown Location")
        self.main_conn_btn.setText("Connect")
        self.main_conn_btn.setStyleSheet("")
        self.stat_labels["Active Connection"].setText("None")
        
        # Reset card highlight
        self.conn_card.setProperty("selected", False)
        self.conn_card.style().unpolish(self.conn_card)
        self.conn_card.style().polish(self.conn_card)
        
        self.refresh_proxy_table()
        self.update_current_info()

    def save_proxy(self):
        ip, port, country, p_type = self.ip_input.text(), self.port_input.text(), self.country_input.text(), self.type_input.currentText()
        if not ip or not port: return
        self.proxy_handler.add_proxy(country, ip, port, p_type, self.user_input.text(), self.pass_input.text())
        self.refresh_proxy_table()
        self.switch_view("proxies")

    def import_proxies(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "Proxy Files (*.txt *.csv)")
        if path and self.proxy_handler.import_proxies(path):
            self.refresh_proxy_table()

    def export_proxies(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export", "proxies.txt", "Text Files (*.txt)")
        if path: self.proxy_handler.export_proxies(path)

    def update_current_info(self):
        info = get_current_ip_info()
        if info and not self.active_proxy:
            self.conn_ip_label.setText(info.get('ip', '---'))
            self.conn_country_label.setText(info.get('country_name', 'Unknown'))

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(qta.icon('fa5s.shield-alt', color='#7C3AED'))
        menu = QMenu()
        menu.addAction("Show").triggered.connect(self.show)
        menu.addAction("Exit").triggered.connect(self.close)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def show_notification(self, title, msg):
        self.tray_icon.showMessage(title, msg, QSystemTrayIcon.Information, 3000)
