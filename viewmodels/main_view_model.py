from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog, QFileSystemModel
from models.local_file_model import LocalFileModel
from models.oci_tree_model import OciTreeModel
from models.transfer_model import TransferModel, TransferItem
from views.local_tree_view import LocalTreeView
from views.oci_tree_view import OciTreeView
import oci, tempfile, os
from models.oci_tree_model import SizeAwareFileSystemModel

class MainViewModel(QObject):
    """Main application controller"""
    # Signals
    local_selection_changed = pyqtSignal(list)
    oci_selection_changed = pyqtSignal(list)
    signal_combo_changed = pyqtSignal(str) 
    signal_combo_activated = pyqtSignal(int)
    status_message = pyqtSignal(str)
    bucket_list_loaded = pyqtSignal(list)  # New signal to emit the bucket list
    oci_root_changed = pyqtSignal(str)

    def __init__(self, local_tree_model, oci_tree_model, transfer_model):
        super().__init__()
        self.local_tree_model = local_tree_model
        self.oci_tree_model = oci_tree_model
        self.transfer_model = transfer_model
        self.config = oci.config.from_file()
        self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage.get_namespace().data
        self.current_bucket = ""
        self.temp_dir = tempfile.TemporaryDirectory(prefix="oci_browser_")

    def change_combo(self, bucket_name):
        print(f"bucket_name: {bucket_name}, type: {type(bucket_name)}")  #
        self.signal_combo_changed.emit(bucket_name)

    def first_load(self, index):
        """Load the OCI TreeView with the selected bucket"""
        self.signal_combo_activated.emit(index)
       
    def load_bucket_combo(self):
        bucket_list = self.oci_tree_model.load_bucket_combo()  # Assuming this method returns a list
        self.bucket_list_loaded.emit(bucket_list)  
        if not bucket_list:  # Check if the bucket list is empty or None
            return "N/D"# Emit the bucket list to the main view
        return bucket_list  # Return the bucket list

    def load_bucket_structure1(self, bucket_name):
        """Update OCI TreeView when bucket selection changes"""
        if bucket_name:     
            try:
                self.oci_tree_model.load_bucket_structure(bucket_name)
                # self.status_message.emit(f"Mostrando bucket: {bucket_name}")
            except Exception as e:
                self.status_message.emit(f"Erro ao carregar bucket: {str(e)}")

    def copy_to_oci(self, selected_files, bucket_name):
        """Delegate the file upload to the OCI Tree Model"""
        self.local_tree_model.copy_to_oci(selected_files, bucket_name)

    def copy_to_local(self, selected_files, bucket_name, local_directory):
        """Delegate the file download to the OCI Tree Model"""
        self.oci_tree_model.copy_to_local(selected_files, bucket_name, local_directory)   

    def load_bucket_structure(self, bucket_name):

        
        self.temp_dir = tempfile.mkdtemp(prefix="oci_browser_")

        # Reset the model
        self.oci_tree_model.beginResetModel()
        self.oci_tree_model.setRootPath(self.temp_dir)
        self.oci_tree_model.endResetModel()

        # Emit signal to update the view's root index
        self.oci_root_changed.emit(self.temp_dir)
        try:
            namespace = self.object_storage.get_namespace().data
            objects = self.object_storage.list_objects(namespace, bucket_name, fields="name,size,timeCreated,storageTier").data.objects
            self.size_map = {}
            # Create the complete folder and file structure
            for obj in objects:
                path_parts = obj.name.split('/')
                current_path = self.temp_dir
                full_path = os.path.join(self.temp_dir, *path_parts)
                self.size_map[full_path] = obj.size  # Store size
                # Create directories
                for part in path_parts[:-1]:  # All parts except last are directories
                    if part:  # Skip empty parts
                        current_path = os.path.join(current_path, part)
                        if not os.path.exists(current_path):
                            os.makedirs(current_path, exist_ok=True)
                
                # Create empty file for the object (last part)
                if path_parts[-1]:  # Only if it's not just a directory path
                    file_path = os.path.join(current_path, path_parts[-1])
                    open(file_path, 'a').close()  # Create empty file
            
            # Set the model root path

            self.oci_tree_model.setRootPath(self.temp_dir)
            self.oci_root_changed.emit(self.temp_dir) 
            
            if hasattr(self, 'oci_tree_model') and isinstance(self.oci_tree_model, SizeAwareFileSystemModel):
                self.oci_tree_model.size_map = self.size_map
                self.oci_tree_model.layoutChanged.emit() 
                
        except Exception as e:
            QMessageBox.critical(self, "OCI Error", f"Failed to load bucket structure: {str(e)}")
