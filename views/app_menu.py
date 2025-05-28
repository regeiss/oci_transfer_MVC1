#===========================================================================================================================================
# -*- coding: utf-8 -*-  # Arquivo: appMenu.py
# Versão: 1.0
# Última alteração: 24/03/2025 - 13:13
# Propósito: Gerar menu para a interface gráfica explorador de arquivos
# Autor: Roberto Edgar Geiss 
# Copyright: PMNH
# Produto: 
# Observacoes:   
# Parametros: 
# Detalhes especificos: 
#===========================================================================================================================================
import os
import sys 
import shutil
from datetime import datetime
from PyQt5.QtWidgets import  QMessageBox, QMenu, QFormLayout, QDialog, QAbstractItemView, QFileIconProvider

from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QIcon, QPixmap, QDrag
from PyQt5.QtWidgets import QMenuBar, QAction, QActionGroup, QMessageBox, QInputDialog, QMenu, QLabel
from PyQt5.QtCore import pyqtSignal
from .proxy_dialog import ProxyConfigDialog
from .oci_config_dialog import OCIConfigDialog  # Ensure this is the correct module path

class AppMenuBar(QMenuBar):
    # Define signals for menu actions
    theme_changed = pyqtSignal(str)  # 'light', 'dark', or 'system'
    about_triggered = pyqtSignal()
    exit_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_menus()

    def setup_menus(self):
        # File Menu
        file_menu = self.addMenu("&Arquivo")
        # file_menu.addAction("&Novo", self.create_folder)
        # file_menu.addAction("A&brir", self.open_file)
        # file_menu.addAction("&Salvar", self.save_file)
        file_menu.addAction("&Login", self.login)
        file_menu.addSeparator()
        file_menu.addAction("&Proxy", self.show_proxy_config)
        file_menu.addAction("Configuração &OCI", self.open_oci_config)
        file_menu.addSeparator()
        file_menu.addAction("Sai&r", self.close_event)

        edit_menu = self.addMenu("&Editar")
        view_menu = self.addMenu("&Visualizar")

        # Help Menu
        help_menu = self.addMenu("&Ajuda")
        help_menu.addAction("&Sobre", self.show_about)
        help_menu.addAction("&Ajuda", self.show_help)
        help_menu.addAction("&Documentação", self.show_documentation)
    
    def show_proxy_config(self):
        """Open the proxy configuration dialog"""
        dialog = ProxyConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Configuração de Proxy", "Configurações de proxy salvas com sucesso.")

    def open_oci_config(self):
        """Open the OCI configuration dialog"""
        dialog = OCIConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Configuração OCI", "Configuração atualizada com sucesso.")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "Sobre", "Explorador de Arquivos OCI\nVersão 0.40.3\nPMNH")   
    def show_help(self):
        """Show help dialog"""

    def show_documentation(self):
        """Show documentation dialog"""
        QMessageBox.information(self, "Documentação", "Documentação não disponível no momento.")
        # You can implement this to show a help file or redirect to a URL   
   
    def close_event(self, event):
        reply = QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit? Any unsaved work will be lost.",
            QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
            QMessageBox.Save)

        if reply == QMessageBox.Close:
            event.accept()
        else:
            event.ignore()

    def login(self):
        """Handle login action"""
        # Implement your login logic here
        QMessageBox.information(self, "Login", "Login action triggered.")
       
class ThumbnailIconProvider(QFileIconProvider):
    def icon(self, info):
        if info.isDir():
            return super().icon(info)
        
        # Handle image thumbnails
        if info.suffix().lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            try:
                pixmap = QPixmap(info.filePath())
                if not pixmap.isNull():
                    return QIcon(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
            except:
                pass
        
        return super().icon(info)       