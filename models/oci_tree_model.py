from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant
from PyQt5.QtGui import QIcon
import oci
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

    def load_bucket_objects(self, bucket_name, prefix=""):
        """Load objects and prefixes (subfolders) for the given bucket and prefix"""
        if not bucket_name:
            return

        try:
            self.beginResetModel()
            self.root_item.children.clear()
            self.current_bucket = bucket_name
            self.current_prefix = prefix

            response = self.object_storage.list_objects(
                namespace_name=self.namespace,
                bucket_name=self.current_bucket,
                prefix=self.current_prefix,
                delimiter="/",
                fields="name,size,timeCreated,storageTier"
            )

            # Add subfolders (prefixes)
            for subfolder in response.data.prefixes:
                folder_name = subfolder.rstrip("/").split("/")[-1]
                folder_item = OCITreeItem(name=folder_name, is_folder=True, parent=self.root_item)
                self.root_item.appendChild(folder_item)

            # Add files
            for obj in response.data.objects:
                if not obj.name.endswith("/"):  # Skip folder placeholders
                    file_name = obj.name.split("/")[-1]
                    file_item = OCITreeItem(
                        name=file_name,
                        is_folder=False,
                        size=obj.size,
                        modified=obj.time_created,
                        parent=self.root_item
                    )
                    self.root_item.appendChild(file_item)

            self.endResetModel()

        except Exception as e:
            self.endResetModel()
            print(f"Error loading bucket objects: {str(e)}")

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

    def data(self, index, role=Qt.DisplayRole):
        """Return the data stored under the given role for the item referred to by the index"""
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:  # Name
                return item.name
            elif index.column() == 1:  # Size
                return self.format_size(item.size) if not item.is_folder else ""
            elif index.column() == 2:  # Modified
                return item.modified.strftime("%Y-%m-%d %H:%M:%S") if item.modified else ""
            elif index.column() == 3:  # Storage Tier
                return item.storage_tier if not item.is_folder else ""

        if role == Qt.DecorationRole and index.column() == 0:
            return QIcon.fromTheme("folder") if item.is_folder else QIcon.fromTheme("text-x-generic")

        return QVariant()
    
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
                return QIcon.fromTheme("folder") if item.is_folder else QIcon.fromTheme("text-x-generic")

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
                return "Standard"  # Default tier

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
    
    def load_bucket_objects(self, bucket_name):
        """Update OCI TreeView when bucket selection changes"""
        if bucket_name:  # Only proceed if a bucket is selected
            try:
                self.beginResetModel()
                self.root_item.children.clear()
                self.current_bucket = bucket_name
                
                response = self.object_storage.list_objects(
                    namespace_name=self.namespace,
                    bucket_name=self.current_bucket,
                    prefix=self.current_prefix,
                    delimiter="/",
                    fields="name, size, timeCreated, storageTier"
                )

                # Create a dictionary to map folder paths to OCITreeItem objects
                folder_map = {self.current_prefix: self.root_item}

                # Add folders (prefixes) to the tree
                for prefix in response.data.prefixes:
                    folder_name = prefix.rstrip("/").split("/")[-1]
                    parent_prefix = "/".join(prefix.rstrip("/").split("/")[:-1]) + "/"
                    parent_item = folder_map.get(parent_prefix, self.root_item)

                    folder_item = OCITreeItem(name=folder_name, is_folder=True)
                    parent_item.appendChild(folder_item)
                    folder_map[prefix] = folder_item

                # Add files to the tree
                for obj in response.data.objects:
                    if not obj.name.endswith('/'):  # Skip folder placeholders
                        file_name = obj.name.split("/")[-1]
                        parent_prefix = "/".join(obj.name.split("/")[:-1]) + "/"
                        parent_item = folder_map.get(parent_prefix, self.root_item)

                        file_item = OCITreeItem(
                            name=file_name,
                            is_folder=False,
                            size=obj.size,
                            modified=obj.time_created,
                            parent=parent_item
                        )
                        parent_item.appendChild(file_item)

                self.data = self.root_item.children
                self.endResetModel()         
                # print(f"Root item children count: {len(self.root_item.children)}") 

            except Exception as e:
                self.endResetModel()
                print(f"Erro ao carregar bucket: {str(e)}")
                

    ###################################################################################################

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