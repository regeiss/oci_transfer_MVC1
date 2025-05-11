import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDir

class OCIConfigDialog(QDialog):
    """Dialog for editing the OCI configuration file"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração OCI")
        self.setMinimumSize(600, 400)

        # Path to the OCI config file
        self.config_path = os.path.join(QDir.homePath(), ".oci", "config")

        # Create layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel(f"Editando arquivo de configuração: {self.config_path}")
        layout.addWidget(self.label)

        # Text editor
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Load the config file
        self.load_config()

        # Connect buttons
        self.save_button.clicked.connect(self.save_config)
        self.cancel_button.clicked.connect(self.reject)

    def load_config(self):
        """Load the OCI config file into the text editor"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as file:
                    self.text_edit.setPlainText(file.read())
            else:
                QMessageBox.warning(self, "Aviso", f"O arquivo de configuração não foi encontrado em {self.config_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo de configuração:\n{str(e)}")

    def save_config(self):
        """Save the contents of the text editor to the OCI config file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as file:
                file.write(self.text_edit.toPlainText())
            QMessageBox.information(self, "Sucesso", "Configuração salva com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar o arquivo de configuração:\n{str(e)}")