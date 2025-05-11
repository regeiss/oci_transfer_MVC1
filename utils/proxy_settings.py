import os
from PyQt5.QtCore import QSettings

def load_proxy_settings():
    """Load proxy settings from QSettings and set environment variables"""
    settings = QSettings("OCITransferApp", "Preferences")
    http_proxy = settings.value("http_proxy", "")
    https_proxy = settings.value("https_proxy", "")

    if http_proxy:
        os.environ['http_proxy'] = http_proxy
        os.environ['HTTP_PROXY'] = http_proxy
    if https_proxy:
        os.environ['https_proxy'] = https_proxy
        os.environ['HTTPS_PROXY'] = https_proxy
