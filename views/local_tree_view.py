from PyQt5.QtWidgets import QTreeView, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from models.local_file_model import LocalFileModel
from views.custom_header_tree_view import CustomHeaderTreeView

class LocalTreeView(CustomHeaderTreeView):
    """View for local file system with custom headers"""
    def __init__(self):
        super().__init__()
        self.setModel(LocalFileModel())
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeView.DragDrop)
        self.setContextMenuPolicy(Qt.CustomContextMenu) 
        # Configure custom headers
        self.set_header_labels(["Nome", "Tamanho", "Tipo", "Data Modificado"])
        self.set_header_sizes([300, 100, 100, 150])
        self.set_header_resize_modes([
            QHeaderView.Stretch,
            QHeaderView.ResizeToContents,
            QHeaderView.ResizeToContents,
            QHeaderView.Interactive
        ])
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.expandAll() #_c_drive()  # Expand C: drive by default

    def get_selected_to_oci(self):
        selected_indexes = self.selectionModel().selectedIndexes()

        # Extract file paths from the selected indexes
        selected_files = []
        for index in selected_indexes:
            if index.column() == 0:  # Only process the first column (file name)
                file_path = self.model().filePath(index)
                selected_files.append(file_path)

        if not selected_files:
            QMessageBox.warning(None, "Erro", "Nenhum arquivo selecionado no ambiente local.")
            return

        return selected_files

    def get_selected_directory(self):
        """Get the currently selected directory in the Local Tree View."""
        selected_indexes = self.selectionModel().selectedIndexes()

        if not selected_indexes:
            QMessageBox.warning(None, "Erro", "Nenhum diretório selecionado no no ambiente local.")
            return None

        # Process only the first selected index
        index = selected_indexes[0]
        if index.isValid():
            # Check if the selected item is a directory
            file_path = self.model().filePath(index)
            if self.model().isDir(index):
                return file_path
            else:
                QMessageBox.warning(None, "Erro", "O item selecionado não é um diretório.")
                return None
        return None

