from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog
from models.local_file_model import LocalFileModel
from models.oci_tree_model import OciTreeModel
from models.transfer_model import TransferModel, TransferItem
from views.local_tree_view import LocalTreeView
from views.oci_tree_view import OciTreeView

class MainViewModel(QObject):
    """Main application controller"""
    # Signals
    local_selection_changed = pyqtSignal(list)
    oci_selection_changed = pyqtSignal(list)
    signal_combo_changed = pyqtSignal(str) 
    signal_combo_activated = pyqtSignal(int)
    status_message = pyqtSignal(str)
    bucket_list_loaded = pyqtSignal(list)  # New signal to emit the bucket list

    def __init__(self, local_tree_model, oci_tree_model, transfer_model):
        super().__init__()
        self.local_tree_model = local_tree_model
        self.oci_tree_model = oci_tree_model
        self.transfer_model = transfer_model

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

    def load_bucket_objects(self, bucket_name):
        """Update OCI TreeView when bucket selection changes"""
        if bucket_name:     
            try:
                self.oci_tree_model.load_bucket_objects(bucket_name)
                # self.status_message.emit(f"Mostrando bucket: {bucket_name}")
            except Exception as e:
                self.status_message.emit(f"Erro ao carregar bucket: {str(e)}")

    def copy_to_oci(self, selected_files, bucket_name):
        """Delegate the file upload to the OCI Tree Model"""
        self.local_tree_model.copy_to_oci(selected_files, bucket_name)

    def copy_to_local(self, selected_files, bucket_name, local_directory):
        """Delegate the file download to the OCI Tree Model"""
        self.oci_tree_model.copy_to_local(selected_files, bucket_name, local_directory)   
