import winreg
import ctypes
import os
import sys

# Constants for InternetSetOption
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37

def refresh_internet_settings():
    """Refresh internet settings using ctypes to apply registry changes immediately."""
    internet_set_option = ctypes.windll.wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)

class WindowsProxyHandler:
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

    @staticmethod
    def set_proxy(ip, port, enabled=True):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsProxyHandler.REG_PATH, 0, winreg.KEY_ALL_ACCESS) as key:
                if enabled:
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{ip}:{port}")
                else:
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            
            refresh_internet_settings()
            return True
        except Exception as e:
            print(f"Error setting proxy: {e}")
            return False

    @staticmethod
    def disable_proxy():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsProxyHandler.REG_PATH, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            
            refresh_internet_settings()
            return True
        except Exception as e:
            print(f"Error disabling proxy: {e}")
            return False

    @staticmethod
    def set_startup(enabled=True):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "ProxyManager"
            app_path = f'"{os.path.abspath(sys.argv[0])}"'
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                if enabled:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"Error setting startup: {e}")
            return False
