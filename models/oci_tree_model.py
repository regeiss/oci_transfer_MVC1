from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, QFileInfo, QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import oci, os, magic
from datetime import datetime
from PyQt5.QtWidgets import QFileSystemModel
from models.size_aware_tree_model import SizeAwareFileSystemModel

class OciTreeModel(SizeAwareFileSystemModel):
    
    def __init__(self):
        self.size_map = {}  # Initialize before calling super().__init__
        super().__init__(self.size_map)

        self.setRootPath(QDir.rootPath())
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""
        self.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries | QDir.Files)
        self.setRootPath(QDir.rootPath())
        # self.namespace = "grhdwpxwta4w"
        # self.current_bucket = "temp-sysnova"
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""
        self.size_map = {}

    def columnCount(self, parent=None):
        # Add 4 columns (Name, Size, Type, Modified)
        return 4

    # def data(self, index, role=Qt.DisplayRole):
    #     if not index.isValid():
    #         return None
    #     # Let QFileSystemModel handle the first column (Name)
    #     if index.column() == 0:
    #         return super().data(index, role)
        
    #     # Handle additional columns
    #     file_info = QFileInfo(self.filePath(index))
        
    #     if index.column() == 1:  # Size column
    #         if role == Qt.DisplayRole:
    #             if not file_info.isDir():
    #                 size = file_info.size()
    #                 return self.format_size(size)
    #             return ""
    #         elif role == Qt.TextAlignmentRole:
    #             return Qt.AlignRight
                
    #     elif index.column() == 2:  # Type column
    #         if role == Qt.DisplayRole:
    #             if file_info.isDir():
    #                 return "Pasta"
    #             return self.get_file_type(file_info.filePath())
                
    #     elif index.column() == 3:  # Modified column
    #         if role == Qt.DisplayRole:
    #             return file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss")
    #         elif role == Qt.TextAlignmentRole:
    #             return Qt.AlignRight
        
    #     return super().data(index, role)

    def get_file_type(self, path):
        """Get human-readable file type"""
        if not os.path.exists(path):
            return ""
        
        if os.path.isdir(path):
            return "Pasta"
            
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

    def load_bucket_combo(self):
        # Initialize the ObjectStorageClient
        namespace = self.object_storage.get_namespace().data
        # compartment_id = self.compartment_id
          
        try:
            list_buckets_response = self.object_storage.list_buckets(
                namespace_name = namespace,#'grhdwpxwta4w', #str(namespace), 
                compartment_id = "ocid1.compartment.oc1..aaaaaaaaoshcb5v3pozme5nt3cg6cymq5bo2nrlyt2vw54en23kamfd5xsda" #compartment_id 
            )

            bucket_list = [bucket.name for bucket in list_buckets_response.data]

        except Exception as e:
            QMessageBox.critical(None, "Erro OCI", f"Erro OCI: {str(e)}")
            raise
    
        return bucket_list
  
    def copy_to_local(self, selected_files, bucket_name, local_directory):
        """Upload selected files to the current OCI bucket"""
        self.current_bucket = bucket_name
        
        if not self.current_bucket:  # Use self.current_bucket directly
            QMessageBox.warning(None, "Erro", "Nenhum bucket selecionado.")
            return
        
        try:
            for object_name in selected_files:
                file_name = os.path.basename(object_name)
                local_path = os.path.join(local_directory, file_name)

                # Download the file from OCI
                response = self.object_storage.get_object(
                    namespace_name=self.namespace_data,
                    bucket_name=self.current_bucket,
                    object_name=object_name
                )
                with open(local_path, "wb") as local_file:
                    local_file.write(response.data.content)

            QMessageBox.information(None, "Sucesso", "Arquivos baixados com sucesso para o diretório local.")
        
        except PermissionError:
            QMessageBox.critical(
                    None,
                    "Erro de Permissão",
                    f"Sem permissão para salvar o arquivo: {local_path}. Verifique as permissões do diretório."
                )

        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao baixar arquivos:\n{str(e)}")

