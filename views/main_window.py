from PyQt5.QtWidgets import (QMainWindow, QSplitter, QPushButton, QVBoxLayout, 
                             QWidget, QComboBox, QDockWidget, QLabel, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from .local_tree_view import LocalTreeView
from .oci_tree_view import OciTreeView
from .transfer_queue_view import TransferQueueView
from .app_menu import AppMenuBar  # Import AppMenuBar from the appropriate module
from .app_toolbar import AppToolBar  # Import AppToolBar from the appropriate module
from viewmodels.main_view_model import MainViewModel

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self, viewmodel):
        super().__init__()
        self._viewmodel = viewmodel
        self._viewmodel.signal_combo_changed.connect(self.bucket_combo_changed)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OCI Transferência de arquivos")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon('resources/icons/folder.ico'))
        # Create main layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create splitter for local and OCI views
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.layout.addWidget(self.splitter)

        self.create_status_bar()
        # Create local file view
        self.local_view = LocalTreeView()
        self.splitter.addWidget(self.local_view)

        # Create OCI view
        self.oci_view = OciTreeView(self._viewmodel)
        self.splitter.addWidget(self.oci_view)

        self.create_controls()
        # # Create transfer queue view
        self.transfer_queue_view = TransferQueueView()
        self.dock_transfer_queue = QDockWidget("Fila de transferência", self)
        self.dock_transfer_queue.setWidget(self.transfer_queue_view)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_transfer_queue)
        self.dock_transfer_queue.setEnabled(False)
        self.dock_transfer_queue.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # Setup menu and toolbar
        self.setup_menu()
        self.setup_toolbar()
        self.setup_layout()

    def setup_menu(self):
        self.menu_bar = AppMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.exit_triggered.connect(self.close)
        
    def setup_toolbar(self):
        self.toolbar = AppToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)     

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Pronto")
        self.status_bar.addPermanentWidget(self.status_label)

    def closeEvent(self, event):
        """Handle the close event of the main window"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Sair")
        msg_box.setText("Você tem certeza que deseja sair?")
        msg_box.setIcon(QMessageBox.Question)

        # Localize the buttons
        yes_button = msg_box.addButton("Sim", QMessageBox.YesRole)
        no_button = msg_box.addButton("Não", QMessageBox.NoRole)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            event.accept()
        else:
            event.ignore()    
        
    def setup_layout(self):
        """Setup the main window layout"""
        # Create button panel
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.bucket_label)
        button_layout.addWidget(self.bucket_combo)
        button_layout.addWidget(self.copy_to_oci_btn)
        button_layout.addWidget(self.copy_from_oci_btn)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.start_queue_btn)
        button_layout.addWidget(self.pause_queue_btn)
        button_layout.addWidget(self.cancel_queue_btn)
        button_layout.addWidget(self.clear_queue_btn)
        
        button_panel = QWidget()
        button_panel.setLayout(button_layout)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.local_view)
        main_splitter.addWidget(button_panel)
        main_splitter.addWidget(self.oci_view)
        main_splitter.setSizes([400, 100, 400])
        
        self.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(main_splitter)

    def create_controls(self):
        """Create control buttons and combo boxes"""
        self.bucket_label = QLabel("Bucket:")
        self.bucket_combo = QComboBox()
        self.bucket_combo.setToolTip("Selecione o bucket")
        self.bucket_combo.setMinimumHeight(28)
        self.bucket_combo.setMinimumWidth(200)
        self.bucket_combo.addItems(self._viewmodel.load_bucket_combo())
        self.bucket_combo.activated.connect(self._viewmodel.first_load)
        self.bucket_combo.currentTextChanged.connect(self._viewmodel.change_combo)
        self.bucket_combo_changed(self.bucket_combo.currentText())  # Load objects for the selected bucket

        # Copy to OCI button
        self.copy_to_oci_btn = QPushButton("→ Copiar para OCI →")
        self.copy_to_oci_btn.setMinimumHeight(30)
        self.copy_to_oci_btn.clicked.connect(self.copy_to_oci_action)  # Connect the button to the action

        # Copy from OCI button
        self.copy_from_oci_btn = QPushButton("← Copiar da OCI ←")
        self.copy_from_oci_btn.setMinimumHeight(30)
        self.copy_from_oci_btn.clicked.connect(self.copy_from_oci_action)

        # Other buttons
        self.up_button = QPushButton("↑ Subir")
        self.up_button.setMinimumHeight(30)
        self.up_button.setEnabled(False)
        self.refresh_btn = QPushButton("Atualizar")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.setEnabled(False)
        self.start_queue_btn = QPushButton("Iniciar Fila")
        self.start_queue_btn.setMinimumHeight(30)
        self.start_queue_btn.setEnabled(False)
        self.start_queue_btn.setToolTip("Iniciar a fila de transferência")
        self.pause_queue_btn = QPushButton("Pausa")
        self.pause_queue_btn.setMinimumHeight(30)
        self.pause_queue_btn.setEnabled(False)
        self.cancel_queue_btn = QPushButton("Cancelar")
        self.cancel_queue_btn.setMinimumHeight(30)
        self.cancel_queue_btn.setEnabled(False)
        self.clear_queue_btn = QPushButton("Limpar Fila")
        self.clear_queue_btn.setMinimumHeight(30)
        self.clear_queue_btn.setEnabled(False)
        self.clear_queue_btn.setToolTip("Limpar a fila de transferência")

    def bucket_combo_changed(self, bucket_name): 
        self._viewmodel.load_bucket_objects(bucket_name)
        # self._viewmodel.setOCIModel(self.oci_view.model())

    def copy_to_oci_action(self):
        # chamar a função copy_to_oci do local view 
        selected_files = self.local_view.get_selected_to_oci()
        if selected_files:
            self._viewmodel.copy_to_oci(selected_files, self.bucket_combo.currentText()) 
            self._viewmodel.load_bucket_objects(self.bucket_combo.currentText())
        else:
            QMessageBox.warning(self, "Erro", "Nenhum arquivo selecionado para copiar.")

    def copy_from_oci_action(self):
        # chamar a função copy_to_oci do local view 
        selected_files = self.oci_view.get_selected_to_local()
        local_directory = self.local_view.get_selected_directory()

        if not local_directory: 
            QFileDialog.getExistingDirectory(self, "Selecione o diretório de destino")
                
        if selected_files:
            self._viewmodel.copy_to_local(selected_files, self.bucket_combo.currentText(), local_directory) 
            # self._viewmodel.load_bucket_objects(self.bucket_combo.currentText())
        else:
            QMessageBox.warning(self, "Erro", "Nenhum arquivo selecionado para copiar.")
