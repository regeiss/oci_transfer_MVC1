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

    # def setup_theme_menu(self, parent_menu):
    #     """Theme selection submenu"""
    #     theme_menu = parent_menu.addMenu("&Theme")
        
    #     theme_group = QActionGroup(self)
    #     theme_group.setExclusive(True)
        
    #     # Light theme
    #     light_action = QAction("Light", self)
    #     light_action.setCheckable(True)
    #     light_action.triggered.connect(lambda: self.theme_changed.emit('light'))
    #     theme_group.addAction(light_action)
    #     theme_menu.addAction(light_action)
        
        # # Dark theme
        # dark_action = QAction("Dark", self)
        # dark_action.setCheckable(True)
        # dark_action.setChecked(True)
        # dark_action.triggered.connect(lambda: self.theme_changed.emit('dark'))
        # theme_group.addAction(dark_action)
        # theme_menu.addAction(dark_action)
        
        # # System theme
        # system_action = QAction("System", self)
        # system_action.setCheckable(True)
        # system_action.triggered.connect(lambda: self.theme_changed.emit('system'))
        # theme_group.addAction(system_action)
        # theme_menu.addAction(system_action)
    
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
        QMessageBox.about(self, "Sobre", "Explorador de Arquivos OCI\nVersão 1.0\nRoberto Edgar Geiss\nPMNH")   
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

    # def open_file(self, path):
    #     """Open file with default application"""
    #     if os.path.isfile(path):
    #         try:
    #             if sys.platform == "win32":
    #                 os.startfile(path)
    #             elif sys.platform == "darwin":
    #                 os.system(f'open "{path}"')
    #             else:
    #                 os.system(f'xdg-open "{path}"')
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    # def show_context_menu(self, pos):
    #     """Show context menu at cursor position"""
    #     menu = QMenu()
        
    #     if self.current_view == "details":
    #         index = self.tree_view.indexAt(pos)
    #     else:
    #         index = self.list_view.indexAt(pos)
        
    #     if index.isValid():
    #         path = self.model.filePath(index)
    #         is_dir = self.model.isDir(index)
            
    #         open_action = menu.addAction("Abrir")
    #         open_action.triggered.connect(lambda: self.open_file(path) if not is_dir else self.navigate_to_path(path))
            
    #         menu.addSeparator()
            
    #         copy_action = menu.addAction("Copiar")
    #         copy_action.triggered.connect(lambda: self.copy_file("copy"))
            
    #         cut_action = menu.addAction("Cortar")
    #         cut_action.triggered.connect(lambda: self.copy_file("cut"))
            
    #         paste_action = menu.addAction("Colar")
    #         paste_action.triggered.connect(self.paste_file)
    #         paste_action.setEnabled(bool(self.clipboard["path"]))
            
    #         menu.addSeparator()
            
    #         delete_action = menu.addAction("Deletar")
    #         delete_action.triggered.connect(self.delete_file)
            
    #         rename_action = menu.addAction("Renomear")
    #         rename_action.triggered.connect(self.rename_file)
            
    #         menu.addSeparator()
            
    #         if is_dir:
    #             new_folder_action = menu.addAction("Nova pasta")
    #             new_folder_action.triggered.connect(self.create_folder)
            
    #         properties_action = menu.addAction("Propriedades")
    #         properties_action.triggered.connect(self.show_properties)
    #     else:
    #         new_folder_action = menu.addAction("Nova pasta")
    #         new_folder_action.triggered.connect(self.create_folder)
            
    #         paste_action = menu.addAction("Colar")
    #         paste_action.triggered.connect(self.paste_file)
    #         paste_action.setEnabled(bool(self.clipboard["path"]))
        
    #     menu.exec_(self.tree_view.viewport().mapToGlobal(pos) if self.current_view == "details" else 
    #               self.list_view.viewport().mapToGlobal(pos))
    
    # def copy_file(self, operation):
    #     """Copy or cut file to clipboard"""
    #     if self.current_view == "details":
    #         index = self.tree_view.currentIndex()
    #     else:
    #         index = self.list_view.currentIndex()
        
    #     if index.isValid():
    #         self.clipboard = {
    #             "operation": operation,
    #             "path": self.model.filePath(index)
    #         }
    
    # def paste_file(self):
    #     """Paste file from clipboard"""
    #     if not self.clipboard["path"]:
    #         return
        
    #     src = self.clipboard["path"]
    #     current_dir = self.model.filePath(self.tree_view.rootIndex())
    #     dst = os.path.join(current_dir, os.path.basename(src))
        
    #     try:
    #         if self.clipboard["operation"] == "copy":
    #             if os.path.isdir(src):
    #                 shutil.copytree(src, dst)
    #             else:
    #                 shutil.copy2(src, dst)
    #         elif self.clipboard["operation"] == "cut":
    #             shutil.move(src, dst)
    #             self.clipboard = {"operation": None, "path": None}
            
    #         # Refresh view
    #         self.model.refresh(self.tree_view.rootIndex())
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Failed to paste: {str(e)}")
    
    # def delete_file(self):
    #     """Delete selected file or folder"""
    #     if self.current_view == "details":
    #         index = self.tree_view.currentIndex()
    #     else:
    #         index = self.list_view.currentIndex()
        
    #     if not index.isValid():
    #         return
        
    #     path = self.model.filePath(index)
    #     confirm = QMessageBox.question(
    #         self, "Confirm Delete", 
    #         f"Are you sure you want to delete '{os.path.basename(path)}'?",
    #         QMessageBox.Yes | QMessageBox.No
    #     )
        
    #     if confirm == QMessageBox.Yes:
    #         try:
    #             if os.path.isdir(path):
    #                 shutil.rmtree(path)
    #             else:
    #                 os.remove(path)
    #             self.model.refresh(index.parent())
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
    
    # def rename_file(self):
    #     """Rename selected file or folder"""
    #     if self.current_view == "details":
    #         index = self.tree_view.currentIndex()
    #         self.tree_view.edit(index)
    #     else:
    #         index = self.list_view.currentIndex()
    #         self.list_view.edit(index)
    
    # def save_file(self):
    #     """Save current file (if applicable)"""
    #     print("Save file functionality not implemented yet.")

    # def create_folder(self):
    #     """Create new folder in current directory"""
    #     current_dir = self.model.filePath(self.tree_view.rootIndex())
    #     folder_name, ok = QInputDialog.getText(
    #         self, "New Folder", "Enter folder name:"
    #     )
        
    #     if ok and folder_name:
    #         try:
    #             new_folder = os.path.join(current_dir, folder_name)
    #             os.makedirs(new_folder, exist_ok=True)
    #             self.model.refresh(self.tree_view.rootIndex())
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}")
    
    # def show_properties(self):
    #     """Show properties of selected file"""
    #     if self.current_view == "details":
    #         index = self.tree_view.currentIndex()
    #     else:
    #         index = self.list_view.currentIndex()
        
    #     if not index.isValid():
    #         return
        
    #     path = self.model.filePath(index)
    #     info = QFileInfo(path)
        
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Properties")
    #     layout = QFormLayout(dialog)
        
    #     layout.addRow("Nome:", QLabel(info.fileName()))
    #     layout.addRow("Caminho:", QLabel(info.path()))
    #     layout.addRow("Tamanho:", QLabel(self.format_size(info.size())))
    #     layout.addRow("Tipo:", QLabel(info.suffix().upper() + " File" if info.suffix() else "File"))
    #     layout.addRow("Criação:", QLabel(info.birthTime().toString()))
    #     layout.addRow("Alterado:", QLabel(info.lastModified().toString()))
        
    #     dialog.exec_()
    
    # def format_size(self, size):
    #     """Format file size in human-readable format"""
    #     for unit in ['B', 'KB', 'MB', 'GB']:
    #         if size < 1024:
    #             return f"{size:.1f} {unit}"
    #         size /= 1024
    #     return f"{size:.1f} TB"
    
    # def update_status(self):
    #     """Update status bar with current directory info"""
    #     current_index = self.tree_view1.rootIndex() if self.current_view == "details" else self.list_view1.rootIndex()
    #     path = self.model.filePath(current_index)
        
    #     if os.path.isdir(path):
    #         try:
    #             num_dirs = 0
    #             num_files = 0
    #             total_size = 0
                
    #             for entry in os.scandir(path):
    #                 if entry.is_dir():
    #                     num_dirs += 1
    #                 else:
    #                     num_files += 1
    #                     total_size += entry.stat().st_size
                
    #             self.status_label.setText(
    #                 f"{num_dirs} folders, {num_files} files, {self.format_size(total_size)}"
    #             )
    #         except PermissionError:
    #             self.status_label.setText("Permission denied")
    #         except Exception as e:
    #             self.status_label.setText(f"Error: {str(e)}")
    #     else:
    #         size = os.path.getsize(path)
    #         self.status_label.setText(f"1 file, {self.format_size(size)}")

    #     self.model.setIconProvider(ThumbnailIconProvider())

    # def search_files(self, text):
    #       """Search files in current directory"""
       
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