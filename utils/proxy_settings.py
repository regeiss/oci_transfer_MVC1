import os
from PyQt5.QtCore import QSettings
from views.proxy_dialog import ProxyConfigDialog  # Adjust the import path as needed

def load_proxy_settings():
    """Load proxy settings from QSettings and set environment variables"""
    settings = QSettings("OCITransferApp", "Preferences")

    if not settings.contains("http_proxy") or not settings.contains("https_proxy"):

        dlg = ProxyConfigDialog()

        if dlg.exec_() != dlg.Accepted:
            return  # User cancelled, do not set proxy
# No proxy settings fou nd, do nothing
        return

    http_proxy = settings.value("http_proxy", "")
    https_proxy = settings.value("https_proxy", "")

    if http_proxy:
        os.environ['http_proxy'] = http_proxy
        os.environ['HTTP_PROXY'] = http_proxy

    if https_proxy:
        os.environ['https_proxy'] = https_proxy
        os.environ['HTTPS_PROXY'] = https_proxy
