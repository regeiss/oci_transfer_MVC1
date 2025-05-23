from PyQt5.QtWidgets import QFileSystemModel, QMessageBox, QFileDialog
from PyQt5.QtCore import QDir, Qt, QFileInfo
from PyQt5.QtGui import QIcon
from views.transfer_progress_dialog import TransferProgressDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
import os, oci, time

class LocalFileModel(QFileSystemModel):
    """Extended model for local file system with additional columns"""
    def __init__(self):
        super().__init__()
        self.setRootPath(QDir.rootPath())
        # self.namespace = "grhdwpxwta4w"
        # self.current_bucket = "temp-sysnova"
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""

    def columnCount(self, parent=None):
        # Add 4 columns (Name, Size, Type, Modified)
        return 4
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        # Let QFileSystemModel handle the first column (Name)
        if index.column() == 0:
            return super().data(index, role)
        
        # Handle additional columns
        file_info = QFileInfo(self.filePath(index))
        
        if index.column() == 1:  # Size column
            if role == Qt.DisplayRole:
                if not file_info.isDir():
                    size = file_info.size()
                    return self.format_size(size)
                return ""
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight
                
        elif index.column() == 2:  # Type column
            if role == Qt.DisplayRole:
                if file_info.isDir():
                    return "Folder"
                return self.get_file_type(file_info.filePath())
                
        elif index.column() == 3:  # Modified column
            if role == Qt.DisplayRole:
                return file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss")
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight
        
        return super().data(index, role)
    
    def get_file_type(self, path):
        """Get human-readable file type"""
        if not os.path.exists(path):
            return ""
        
        if os.path.isdir(path):
            return "Folder"
            
        # Use python-magic or file extension as fallback
        try:
            import magic
            mime = magic.Magic(mime=True)
            return mime.from_file(path).split('/')[-1].capitalize()
        except:
            ext = os.path.splitext(path)[1]
            if ext:
                return ext[1:].upper() + " File"
            return "File"
    
    def format_size(self, size):
        """Format file size in human-readable format"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024*1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024*1024*1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.1f} GB"
    
    def get_path(self, index):
        """Get full path for a given index"""
        return self.filePath(index)
    
    def refresh(self, path=None):
        """Refresh the model"""
        if path is None:
            path = self.rootPath()
        self.setRootPath("")  # This forces a refresh
        self.setRootPath(path)
        # self.expand_c_drive()  # Expand C: drive again if needed    
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            headers = ["Nome", "Tamanho", "Tipo", "Data Modificado"]
            if section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)
    
    def copy_to_oci(self, selected_files, bucket_name):
        """Upload selected files to the current OCI bucket with progress dialog"""
        self.current_bucket = bucket_name

        if not self.current_bucket:
            QMessageBox.warning(None, "Erro", "Nenhum bucket selecionado.")
            return

        total_files = len(selected_files)
        dialog = TransferProgressDialog(total_files, qapp=QApplication.instance())
        dialog.show()

        try:
            copy_cancelled = False
            for idx, file_path in enumerate(selected_files, 1):
                if dialog.cancelled:
                    QMessageBox.information(None, "Cancelado", "Transferência cancelada pelo usuário.")
                    break

                file_name = os.path.basename(file_path)

                # Check if file already exists in the bucket
                try:
                    self.object_storage.get_object(
                        namespace_name=self.namespace,
                        bucket_name=bucket_name,
                        object_name=file_name
                    )
                    # If no exception, file exists
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Arquivo já existe no OCI")
                    msg_box.setText(f"O arquivo '{file_name}' já existe no bucket. Deseja sobrescrever?")
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    yes_button = msg_box.button(QMessageBox.Yes)
                    no_button = msg_box.button(QMessageBox.No)
                    yes_button.setText(QCoreApplication.translate("QMessageBox", "Sim"))
                    no_button.setText(QCoreApplication.translate("QMessageBox", "Não"))
                    reply = msg_box.exec_()

                    if reply == QMessageBox.No:
                        dialog.update_file_progress(0)
                        dialog.update_total_progress(idx, total_files, file_name)
                        dialog.qapp.processEvents()
                        copy_cancelled = True
                        continue  # Skip this file
                    else:
                        copy_cancelled = False

                except oci.exceptions.ServiceError as e:
                    if e.status != 404:
                        # If it's not a "not found" error, re-raise
                        raise

                file_size = os.path.getsize(file_path)
                total_read = 0
                chunk_size = 1024 * 1024  # 1MB

                with open(file_path, "rb") as file_data:
                    wrapped_file = ProgressFileWrapper(file_data, file_size, dialog, idx, total_files, file_name)
                    self.object_storage.put_object(
                        namespace_name=self.namespace,
                        bucket_name=bucket_name,
                        object_name=file_name,
                        put_object_body=wrapped_file
                    )

                dialog.update_file_progress(0)
                dialog.update_total_progress(idx, total_files, file_name)
                dialog.qapp.processEvents()

            dialog.close()
            if not dialog.cancelled and not copy_cancelled:
                QMessageBox.information(None, "Sucesso", "Arquivos enviados com sucesso para o OCI.")

        except Exception as e:
            dialog.close()
            QMessageBox.critical(None, "Erro", f"Erro ao enviar arquivos:\n{str(e)}")

class ProgressFileWrapper:
    def __init__(self, file_obj, file_size, dialog, idx, total_files, file_name):
        self.file_obj = file_obj
        self.file_size = file_size
        self.dialog = dialog
        self.idx = idx
        self.total_files = total_files
        self.file_name = file_name
        self.total_read = 0

    def read(self, size=-1):
        # PAUSE/RESUME SUPPORT
        while self.dialog.paused and not self.dialog.cancelled:
            self.dialog.qapp.processEvents()
            time.sleep(0.1)
        if self.dialog.cancelled:
            return b""

        chunk = self.file_obj.read(size)
        self.total_read += len(chunk)
        if self.file_size > 0:
            percent = int((self.total_read / self.file_size) * 100)
        else:
            percent = 0
        self.dialog.update_file_progress(percent)
        self.dialog.label.setText(
            f"Enviando: {self.file_name} ({self.idx}/{self.total_files}) - {self.total_read // 1024} KB"
        )
        self.dialog.qapp.processEvents()
        return chunk

    def __getattr__(self, attr):
        return getattr(self.file_obj, attr)
