import sys
from PyQt5.QtWidgets import QApplication
from models.local_file_model import LocalFileModel
from models.oci_tree_model import OciTreeModel
from models.transfer_model import TransferModel
from views.main_window import MainWindow
from views.oci_tree_view import OciTreeView  # Import OciTreeView
from views.local_tree_view import LocalTreeView  # Import LocalTreeView
from viewmodels.main_view_model import MainViewModel  # Import MainViewModel
from views.oci_tree_view import OciTreeView
from utils.proxy_settings import load_proxy_settings
from PyQt5.QtCore import QSettings

def main():
    app = QApplication(sys.argv)
    load_proxy_settings()
    
    # Initialize models
    local_model = LocalFileModel()
    oci_tree_model = OciTreeModel()
    transfer_model = TransferModel()
    
    # Create the viewmodel and pass the oci_tree_view
    viewmodel = MainViewModel(local_model, oci_tree_model, transfer_model)  # Pass the local_tree_view as well
    window = MainWindow(viewmodel)  # Create the MainWindow first
  
    # main_controller.status_message.connect(window.status_label.setText)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()