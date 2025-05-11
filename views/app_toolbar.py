#===========================================================================================================================================
# -*- coding: utf-8 -*-  # Arquivo: pyExpQt.py
# Versão: 1.0
# Última alteração: 02/04/2025 - 17:13
# Propósito: Gerar toolbar para o explorador de arquivos OCI
# Autor: Roberto Edgar Geiss 
# Copyright: PMNH
# Produto: 
# Observacoes:   
# Parametros: 
# Detalhes especificos: 
#===========================================================================================================================================
from PyQt5.QtWidgets import QToolBar, QAction, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize
# from views.dark_theme import set_dark_theme 

class AppToolBar(QToolBar):
   
    # Define signals for toolbar actions
    new_triggered = pyqtSignal()
    open_triggered = pyqtSignal()
    save_triggered = pyqtSignal()
    theme_changed = pyqtSignal(str)  # 'light' or 'dark'
    
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setup_actions()
        self.setup_toolbar()
        self.dark_mode = False

    def setup_actions(self):
        # New action
        self.new_action = self.addAction(QIcon("resources/icons/account_circle_24dp_E3E3E3.svg"), "New")
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_triggered.emit)

        # Open action
        self.open_action = self.addAction(QIcon("resources/icons/home_24dp_E3E3E3.svg"), "Open")
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_triggered.emit)

        # Save action
        self.save_action = self.addAction(QIcon("resources/icons/settings_24dp_E3E3E3.svg"), "Save")
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_triggered.emit)

        # Separator
        self.separator = self.addSeparator()

        # Theme toggle action
       
    def setup_toolbar(self):
        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addSeparator()
        # self.addAction(self.theme_action)

    def create_theme_toggle(self):
        """Add theme toggle button to toolbar"""
        theme_action = QAction("🌓", self)  # Moon/sun symbol
        theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_action)

    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.dark_mode = not self.dark_mode
        app = self.instance()
        
        # if self.dark_mode:
        #     set_dark_theme(app)
        # else:
        #     app.setPalette(app.style().standardPalette())  # Reset to default
        #     app.setStyle("Fusion")  # Keep Fusion style for consistency
        
        # self.update_icons()

# EOF        