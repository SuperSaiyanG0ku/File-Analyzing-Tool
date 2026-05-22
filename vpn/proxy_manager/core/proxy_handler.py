import csv
from .db_manager import DatabaseManager
from .windows_proxy import WindowsProxyHandler

class ProxyHandler:
    def __init__(self):
        self.db = DatabaseManager()
        self.windows_proxy = WindowsProxyHandler()

    def add_proxy(self, country, ip, port, proxy_type, username="", password=""):
        self.db.add_proxy(country, ip, port, proxy_type, username, password)

    def get_proxies(self):
        return self.db.get_all_proxies()

    def delete_proxy(self, proxy_id):
        self.db.delete_proxy(proxy_id)

    def connect_proxy(self, ip, port):
        return self.windows_proxy.set_proxy(ip, port)

    def disconnect_proxy(self):
        return self.windows_proxy.disable_proxy()

    def import_proxies(self, file_path):
        """Import proxies from TXT or CSV."""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.csv'):
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2: # ip, port
                            ip, port = row[0], row[1]
                            country = row[2] if len(row) > 2 else "Unknown"
                            proxy_type = row[3] if len(row) > 3 else "HTTP"
                            user = row[4] if len(row) > 4 else ""
                            pw = row[5] if len(row) > 5 else ""
                            self.add_proxy(country, ip, port, proxy_type, user, pw)
                else: # TXT format: ip:port or ip:port:user:pass
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            ip, port = parts[0], parts[1]
                            user = parts[2] if len(parts) > 2 else ""
                            pw = parts[3] if len(parts) > 3 else ""
                            self.add_proxy("Unknown", ip, port, "HTTP", user, pw)
            return True
        except Exception as e:
            print(f"Error importing proxies: {e}")
            return False

    def export_proxies(self, file_path):
        """Export proxies to TXT."""
        try:
            proxies = self.get_proxies()
            with open(file_path, 'w') as f:
                for p in proxies:
                    # p = (id, country, ip, port, user, pass, type)
                    line = f"{p[2]}:{p[3]}"
                    if p[4] and p[5]:
                        line += f":{p[4]}:{p[5]}"
                    f.write(line + '\n')
            return True
        except Exception as e:
            print(f"Error exporting proxies: {e}")
            return False
