from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import oci, os, magic
from datetime import datetime
from models.oci_tree_item import OCITreeItem

class OciTreeModel(QAbstractItemModel):
    """Extended model for OCI bucket contents with hierarchical structure"""
    def __init__(self):
        super().__init__()
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""
        self.current_prefix = ""
        self.root_item = OCITreeItem("Root", is_folder=True)

    def index(self, row, column, parent=QModelIndex()):
        """Return the index of the item in the model specified by row, column, and parent"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        """Return the parent of the item with the given index"""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        if not child_item or not child_item.parent_item:
            return QModelIndex()

        parent_item = child_item.parent_item
        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows under the given parent"""
        if not parent.isValid():
            return len(self.root_item.children)

        parent_item = parent.internalPointer()
        return len(parent_item.children) if parent_item else 0

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns for the children of the given parent"""
        return 4  # Name, Size, Modified, Tier

    def flags(self, index):
        default_flags = super().flags(index)
        return default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
    
    def format_size(self, size):
        """Format size in bytes to a human-readable format"""
        if size is None:
            return ""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        
        # print(f"Accessing data for item: {item.name}, row: {index.row()}, column: {index.column()}, role: {role}")  # Debug statement
        if index.column() == 0:  # Name column
            if role == Qt.DisplayRole:
                return item.name
            if role == Qt.DecorationRole:
                return QIcon('resources/icons/folder.svg') if item.is_folder else (QIcon('resources/icons/file.svg'))

        elif index.column() == 1:  # Size column
            if role == Qt.DisplayRole and not item.is_folder:
                return self.format_size(item.size)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight

        elif index.column() == 2:  # Modified column
            if role == Qt.DisplayRole and not item.is_folder:
                return item.modified.strftime('%Y-%m-%d %H:%M:%S') if item.modified else ""

        elif index.column() == 3:  # Storage tier column
            if role == Qt.DisplayRole and not item.is_folder:
                return item.storage_tier

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            headers = ["Objeto", "Tamanho", "Data", "Storage Tier"]
            if section < len(headers):
                return headers[section]
        return QVariant()

    def load_bucket_combo(self):
        # Initialize the ObjectStorageClient
        namespace = self.object_storage.get_namespace().data
        compartment_id = self.config["tenancy"]
          
        try:
            list_buckets_response = self.object_storage.list_buckets(
                namespace_name = 'grhdwpxwta4w', #str(namespace), 
                compartment_id = 'ocid1.compartment.oc1..aaaaaaaaoshcb5v3pozme5nt3cg6cymq5bo2nrlyt2vw54en23kamfd5xsda'#str(compartmentid)  
            )

            bucket_list = [bucket.name for bucket in list_buckets_response.data]

        except Exception as e:
            self.status_message.emit(f"Erro OCI: {str(e)}")
            raise
    
        return bucket_list
  
    def load_bucket_objects(self, bucket_name, prefix=""):
        """Update OCI TreeView when bucket selection or folder changes."""
        if not bucket_name:
            return

        def add_items(parent_item, current_prefix):
            response = self.object_storage.list_objects(
                namespace_name=self.namespace,
                bucket_name=bucket_name,
                prefix=current_prefix,
                delimiter="/",
                fields="name,size,timeCreated,storageTier"
            )

            # Add folders (prefixes)
            for folder_prefix in response.data.prefixes:
                folder_name = folder_prefix.rstrip("/").split("/")[-1]
                folder_item = OCITreeItem(name=folder_name, is_folder=True, full_name=folder_prefix, parent=parent_item)
                parent_item.appendChild(folder_item)
                # Recursively add subfolders and files
                add_items(folder_item, folder_prefix)

            # Add files directly under current_prefix
            for obj in response.data.objects:
                if not obj.name.endswith('/'):  # Skip folder placeholders
                    file_name = obj.name.split("/")[-1]
                    file_item = OCITreeItem(
                        name=file_name,
                        is_folder=False,
                        size=obj.size,
                        modified=obj.time_created,
                        parent=parent_item,
                        full_name=obj.name,
                        storage_tier=getattr(obj, "storage_tier", None)
                    )
                    parent_item.appendChild(file_item)

        try:
            print(f"Loading bucket: {bucket_name}, prefix: {prefix}")
            self.beginResetModel()
            self.root_item.children.clear()
            self.current_bucket = bucket_name
            self.current_prefix = prefix

            add_items(self.root_item, prefix)

            self.data = self.root_item.children
            self.endResetModel()
            print(f"Tree successfully loaded. Root children count: {len(self.root_item.children)}")
        except Exception as e:
            self.endResetModel()
            print(f"Erro ao carregar bucket: {str(e)}")

    def copy_to_local(self, selected_files, bucket_name, local_directory):
        """Download selected files from the current OCI bucket, preserving subfolder structure."""
        self.current_bucket = bucket_name

        if not self.current_bucket:
            QMessageBox.warning(None, "Erro", "Nenhum bucket selecionado.")
            return

        try:
            for object_name in selected_files:
                # Recreate the subfolder structure locally
                relative_path = object_name  # object_name is the full path in the bucket
                local_path = os.path.join(local_directory, relative_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Download the file from OCI
                response = self.object_storage.get_object(
                    namespace_name=self.namespace,
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
    # def get_path(self, index):  
    #     """Get full path for a given index"""
    #     if not index.isValid():
    #         return ""
    #     item = index.internalPointer()
    #     return item.path if item else ""
    # def get_item(self, index):
    #     """Get the item at the given index"""
    #     if not index.isValid():
    #         return None
    #     return index.internalPointer()
    # def get_item_by_path(self, path):   
    #     """Get the item by its path"""
    #     for item in self.root_item.children:
    #         if item.path == path:
    #             return item
    #     return None
    # def get_item_by_name(self, name):       
    #     """Get the item by its name"""
    #     for item in self.root_item.children:
    #         if item.name == name:
    #             return item
    #     return None
    # def get_item_by_index(self, index):       
    #     """Get the item by its index"""
    #     if not index.isValid():
    #         return None
    #     return index.internalPointer()
    # def get_item_by_row(self, row):      
    #     """Get the item by its row"""
    #     if row < 0 or row >= self.root_item.childCount():
    #         return None
    #     return self.root_item.child(row)        
    # def get_item_by_column(self, column):               
    #     """Get the item by its column"""
    #     if column < 0 or column >= self.columnCount():
    #         return None
    #     return self.root_item.child(column)
    # def get_item_by_parent(self, parent):
    #     """Get the item by its parent"""
    #     if not parent.isValid():
    #         return None
    #     return parent.internalPointer()
    # def get_item_by_parent_row(self, parent, row):                                  
    #     """Get the item by its parent and row"""
    #     if not parent.isValid():
    #         return None
    #     parent_item = parent.internalPointer()
    #     if row < 0 or row >= parent_item.childCount():
    #         return None
    #     return parent_item.child(row)