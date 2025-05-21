from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, QFileInfo, QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import oci, os, magic
from datetime import datetime
from PyQt5.QtWidgets import QFileSystemModel
from models.size_aware_tree_model import SizeAwareFileSystemModel
import tempfile
import os
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime

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
        self.namespace = "grhdwpxwta4w"
        # self.current_bucket = "temp-sysnova"
        self.size_map = {}
        self.path_to_object_name = {}
        
    def columnCount(self, parent=None):
        # Add 4 columns (Name, Size, Type, Modified)
        return 4

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            headers = ["Nome", "Tamanho", "Tipo", "Data Modificado"]
            if 0 <= section < len(headers):
                return headers[section]
            
        return super().headerData(section, orientation, role)
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == 1:  # Size column
            file_path = os.path.abspath(self.filePath(index))
            if file_path in self.size_map:
                return self.format_size(self.size_map[file_path])
        return super().data(index, role)
   
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
        """Download selected files from the current OCI bucket"""
        self.current_bucket = bucket_name

        if not self.current_bucket:
            QMessageBox.warning(None, "Erro", "Nenhum bucket selecionado.")
            return

        try:
            for local_path in selected_files:
                # Map local temp file path to object name in bucket
                object_name = self.path_to_object_name.get(os.path.abspath(local_path))
                if not object_name:
                    continue  # Skip if not found

                file_name = os.path.basename(object_name)
                dest_path = os.path.join(local_directory, file_name)

                # Download the file from OCI
                response = self.object_storage.get_object(
                    namespace_name=self.namespace,
                    bucket_name=self.current_bucket,
                    object_name=object_name
                )
                with open(dest_path, "wb") as local_file:
                    local_file.write(response.data.content)

            QMessageBox.information(None, "Sucesso", "Arquivos baixados com sucesso para o diretório local.")

        except PermissionError:
            QMessageBox.critical(
                None,
                "Erro de Permissão",
                f"Sem permissão para salvar o arquivo: {dest_path}. Verifique as permissões do diretório."
            )

        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao baixar arquivos:\n{str(e)}")

    def load_bucket_structure(self, object_storage, namespace, bucket_name):
        """Populate the model with the structure of the selected OCI bucket."""
        temp_dir = tempfile.mkdtemp(prefix="oci_browser_")
        self.beginResetModel()
        self.setRootPath(temp_dir)
        self.endResetModel()

        try:
            objects = object_storage.list_objects(
                namespace, bucket_name, fields="name,size,timeCreated,storageTier"
            ).data.objects
            size_map = {}
            date_map = {}
            for obj in objects:
                path_parts = obj.name.split('/')
                full_path = os.path.join(temp_dir, *path_parts)
                abs_path = os.path.abspath(full_path)
                size_map[abs_path] = obj.size
                self.path_to_object_name[abs_path] = obj.name  # <-- Add this line
                # Parse and store the date/time
                if hasattr(obj, "time_created"):
                    # OCI returns datetime.datetime object, but if it's a string, parse it
                    dt = obj.time_created
                    if isinstance(dt, str):
                        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                    date_map[abs_path] = dt
                current_path = temp_dir
                for part in path_parts[:-1]:
                    if part:
                        current_path = os.path.join(current_path, part)
                        if not os.path.exists(current_path):
                            os.makedirs(current_path, exist_ok=True)
                if path_parts[-1]:
                    file_path = os.path.join(current_path, path_parts[-1])
                    open(file_path, 'a').close()
            self.setRootPath(temp_dir)
            self.size_map = size_map
            self.date_map = date_map  # <-- Store the date map
            self.layoutChanged.emit()
            return temp_dir
        
        except Exception as e:
            QMessageBox.critical(None, "OCI Error", f"Failed to load bucket structure: {str(e)}")
            return None

