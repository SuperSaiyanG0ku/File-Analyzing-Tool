import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal

class ProxyTester(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, proxy_data):
        super().__init__()
        self.proxy_data = proxy_data

    def run(self):
        ip = self.proxy_data['ip']
        port = self.proxy_data['port']
        proxy_type = self.proxy_data['proxy_type'].lower()
        username = self.proxy_data.get('username', '')
        password = self.proxy_data.get('password', '')

        proxy_url = ""
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{ip}:{port}"
        else:
            proxy_url = f"{proxy_type}://{ip}:{port}"

        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        result = {
            "id": self.proxy_data.get('id'),
            "status": "Offline",
            "ping": "N/A"
        }

        try:
            start_time = time.time()
            # Use a fast-responding URL for testing
            response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
            ping = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                result["status"] = "Online"
                result["ping"] = f"{ping}ms"
        except Exception:
            pass

        self.finished.emit(result)

def get_current_ip_info():
    """Get current public IP and location info."""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None
