from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, QFileInfo, QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import oci, os, magic
from datetime import datetime
from PyQt5.QtWidgets import QFileSystemModel
import tempfile

class OciTreeModel(QFileSystemModel):
    
    def __init__(self):
        super().__init__()
        self.setRootPath(QDir.rootPath())
        # self.namespace = "grhdwpxwta4w"
        # self.current_bucket = "temp-sysnova"
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""
        self.temp_dir = tempfile.mkdtemp(prefix="oci_browser_")

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
    
    # def load_bucket_objects(self, bucket_name, prefix=""):
    #     """Update OCI TreeView when bucket selection or folder changes."""
    #     if bucket_name:  # Only proceed if a bucket is selected
    #         try:
    #             print(f"Loading bucket: {bucket_name}, prefix: {prefix}")  # Debug print
    #             self.beginResetModel()
    #             if prefix == "":
    #                 self.root_item.children.clear()  # Clear only for root-level loading
    #             self.current_bucket = bucket_name
    #             self.current_prefix = prefix

    #             response = self.object_storage.list_objects(
    #                 namespace_name=self.namespace_data,
    #                 bucket_name=self.current_bucket,
    #                 prefix=self.current_prefix,
    #                 delimiter="/",
    #                 fields="name, size, timeCreated, storageTier"
    #             )

    #             # Debug: Print response data
    #             print(f"Prefixes: {response.data.prefixes}")
    #             print(f"Objects: {[obj.name for obj in response.data.objects]}")

    #             # Create a dictionary to map folder paths to OCITreeItem objects
    #             folder_map = {self.current_prefix: self.root_item}

    #             # Add folders (prefixes) to the tree
    #             for prefix in response.data.prefixes:
    #                 folder_name = prefix.rstrip("/").split("/")[-1]
    #                 parent_prefix = "/".join(prefix.rstrip("/").split("/")[:-1]) + "/"
    #                 parent_item = folder_map.get(parent_prefix, self.root_item)

    #                 folder_item = OCITreeItem(name=folder_name, is_folder=True, full_name=prefix)
    #                 parent_item.appendChild(folder_item)
    #                 folder_map[prefix] = folder_item

    #             # Add files to the tree
    #             for obj in response.data.objects:
    #                 if not obj.name.endswith('/'):  # Skip folder placeholders
    #                     file_name = obj.name.split("/")[-1]
    #                     parent_prefix = "/".join(obj.name.split("/")[:-1]) + "/"
    #                     parent_item = folder_map.get(parent_prefix, self.root_item)

    #                     if parent_item is None:
    #                         print(f"Warning: Parent item not found for file {file_name}")  # Debug print
    #                         continue

    #                     file_item = OCITreeItem(
    #                         name=file_name,
    #                         is_folder=False,
    #                         size=obj.size,
    #                         modified=obj.time_created,
    #                         parent=parent_item,
    #                         full_name=obj.name  # Full object name
    #                     )
    #                     parent_item.appendChild(file_item)

    #             self.data = self.root_item.children
    #             self.endResetModel()
    #             print(f"Tree successfully loaded. Root children count: {len(self.root_item.children)}") 
    #              # Debug print
    #         except Exception as e:
    #             self.endResetModel()
    #             print(f"Erro ao carregar bucket: {str(e)}")

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