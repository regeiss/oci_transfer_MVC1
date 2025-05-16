from PyQt5.QtWidgets import QFileSystemModel, QMessageBox, QFileDialog
from PyQt5.QtCore import QDir, Qt, QFileInfo
from PyQt5.QtGui import QIcon
import os, oci

class LocalFileModel(QFileSystemModel):
    """Extended model for local file system with additional columns"""
    def __init__(self):
        super().__init__()
        self.setRootPath(QDir.rootPath())
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
        """Upload selected files to the current OCI bucket"""
        self.current_bucket = bucket_name
        
        if not self.current_bucket:  # Use self.current_bucket directly
            QMessageBox.warning(None, "Erro", "Nenhum bucket selecionado.")
            return

        try:
            for file_path in selected_files:
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as file_data:
                    # Perform the upload to OCI
                    self.object_storage.put_object(
                        namespace_name=self.namespace,
                        bucket_name=bucket_name,
                        object_name=file_name,
                        put_object_body=file_data
                    )
            QMessageBox.information(None, "Sucesso", "Arquivos enviados com sucesso para o OCI.")
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao enviar arquivos:\n{str(e)}")
