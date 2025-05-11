from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import QSettings

class ProxyConfigDialog(QDialog):
    """Dialog for configuring proxy settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração de Proxy")
        self.setMinimumSize(400, 200)

        # Create layout
        layout = QVBoxLayout()

        # Proxy fields
        self.http_proxy_label = QLabel("HTTP Proxy:")
        self.http_proxy_input = QLineEdit()
        self.https_proxy_label = QLabel("HTTPS Proxy:")
        self.https_proxy_input = QLineEdit()

        # Load existing settings
        self.load_settings()

        # Add fields to layout
        layout.addWidget(self.http_proxy_label)
        layout.addWidget(self.http_proxy_input)
        layout.addWidget(self.https_proxy_label)
        layout.addWidget(self.https_proxy_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)

    def load_settings(self):
        """Load proxy settings from QSettings"""
        settings = QSettings("OCITransferApp", "Preferences")
        self.http_proxy_input.setText(settings.value("http_proxy", ""))
        self.https_proxy_input.setText(settings.value("https_proxy", ""))

    def save_settings(self):
        """Save proxy settings to QSettings"""
        settings = QSettings("OCITransferApp", "Preferences")
        settings.setValue("http_proxy", self.http_proxy_input.text())
        settings.setValue("https_proxy", self.https_proxy_input.text())
        self.accept()