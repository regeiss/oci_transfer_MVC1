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
    """Verify if the OCI config file exists. If not, create it with default content and notify the user. Then open it for editing using OCIConfigDialog."""
    import os
    import sys
    from PyQt5.QtWidgets import QMessageBox, QApplication
    from views.oci_config_dialog import OCIConfigDialog  # Adjust import if needed

    oci_config_path = os.path.expanduser("~/.oci/config")
    default_content = (
        "[DEFAULT]\n"
        "user=\n"
        "fingerprint=\n"
        "tenancy=\n"
        "region=sa-saopaulo-1\n"
        "compartment_id=\n"
        "namespace=\n"
        "key_file=\n"
    )
    if not os.path.isfile(oci_config_path):
        # Try to create the directory if it doesn't exist
        oci_config_dir = os.path.dirname(oci_config_path)
        try:
            os.makedirs(oci_config_dir, exist_ok=True)
            with open(oci_config_path, "w", encoding="utf-8") as f:
                f.write(default_content)
        except Exception as e:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Erro ao criar configuração OCI",
                f"Não foi possível criar o arquivo de configuração OCI em:\n{oci_config_path}\nErro: {e}\nO aplicativo será encerrado."
            )
            sys.exit(1)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        QMessageBox.information(
            None,
            "Configuração OCI criada",
            f"O arquivo de configuração OCI não existia e foi criado em:\n{oci_config_path}\nEdite este arquivo com suas credenciais antes de usar o aplicativo."
        )
        # Open the OCI config dialog for editing
        dlg = OCIConfigDialog()
        dlg.exec_()

