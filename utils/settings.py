import os
import sys
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMessageBox
from views.proxy_dialog import ProxyConfigDialog  # Adjust the import path as needed

def load_proxy_settings():
    """Load proxy settings from QSettings and set environment variables. Exit if not set."""
    settings = QSettings("OCITransferApp", "Preferences")

    http_proxy = settings.value("http_proxy", "")
    https_proxy = settings.value("https_proxy", "")

    if not http_proxy and not https_proxy:
        dlg = ProxyConfigDialog()
        if dlg.exec_() != dlg.Accepted:
            # Show message and exit if user cancels
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            QMessageBox.critical(None, "Proxy obrigatório", "Configuração de proxy não informada. O aplicativo será encerrado.")
            sys.exit(1)
        # Reload settings after dialog
        http_proxy = settings.value("http_proxy", "")
        https_proxy = settings.value("https_proxy", "")
        if not http_proxy and not https_proxy:
            QMessageBox.critical(None, "Proxy obrigatório", "Configuração de proxy não informada. O aplicativo será encerrado.")
            sys.exit(1)

    if http_proxy:
        os.environ['http_proxy'] = http_proxy
        os.environ['HTTP_PROXY'] = http_proxy

    if https_proxy:
        os.environ['https_proxy'] = https_proxy
        os.environ['HTTPS_PROXY'] = https_proxy

def verify_oci_config():
    """Verify if the OCI config file exists. Exit if not found."""
    import os
    import sys
    from PyQt5.QtWidgets import QMessageBox, QApplication

    oci_config_path = os.path.expanduser("~/.oci/config")
    if not os.path.isfile(oci_config_path):
        app = QApplication.instance()
        if app is None:
            from PyQt5.QtWidgets import QApplication
            import sys
            app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Configuração OCI ausente",
            f"O arquivo de configuração OCI não foi encontrado em:\n{oci_config_path}\nO aplicativo será encerrado."
        )
        sys.exit(1)

