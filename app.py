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
from utils.settings import load_proxy_settings, verify_oci_config
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
import os

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'br.gov.rs.pmhn.oci_transferencia'  # Set this to a unique ID for your app
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OCI Transferência de Arquivos")
    app.setOrganizationName("PMNH")
    app.setOrganizationDomain("pmnh.gov.br")
    app.setApplicationVersion("0.4.3")
    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'folder.ico')))
    load_proxy_settings()
    verify_oci_config()
    
    local_model = LocalFileModel()
    oci_tree_model = OciTreeModel()
    transfer_model = TransferModel()
    
    viewmodel = MainViewModel(local_model, oci_tree_model, transfer_model)  # Pass the local_tree_view as well
    window = MainWindow(viewmodel)  # Create the MainWindow first
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()