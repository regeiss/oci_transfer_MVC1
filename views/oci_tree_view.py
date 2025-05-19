from PyQt5.QtWidgets import QTreeView, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, QFileInfo, QModelIndex
from models.oci_tree_model import OciTreeModel
from views.custom_header_tree_view import CustomHeaderTreeView
import os

class OciTreeView(CustomHeaderTreeView):
    """View for local file system with custom headers"""
    def __init__(self, viewmodel):
        super().__init__()
        self._viewmodel = viewmodel
        self.setModel(self._viewmodel.oci_tree_model)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeView.DragDrop)
        self.setContextMenuPolicy(Qt.CustomContextMenu) 
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        # self.adjust_column_widths()
        # self.model().modelReset.connect(self.adjust_column_widths)
         # Configure custom headers
        self.set_header_labels(["Nome", "Tamanho", "Tipo", "Data Modificado"])
        self.set_header_sizes([300, 100, 100, 150])
        self.set_header_resize_modes([
            QHeaderView.ResizeToContents,
            QHeaderView.ResizeToContents,
            QHeaderView.Stretch,
            QHeaderView.Stretch
        ])

         # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.expandAll() #_c_drive()  # Expand C: drive by default
    
    def get_selected_to_local(self):
        """Get the list of files selected in the OCI tree."""
        selected_indexes = self.selectionModel().selectedIndexes()

        # Extract file paths from the selected indexes
        selected_files = []
        for index in selected_indexes:
            if index.column() == 0:  # Only process the first column (file name)
                item = index.internalPointer()
                if not item.is_folder:  # Only include files
                    selected_files.append(item.name)

        if not selected_files:
            QMessageBox.warning(None, "Erro", "Nenhum arquivo selecionado no Oci Tree View.")
            return

        return selected_files

    def on_item_double_clicked(self, index: QModelIndex):
        source_index = self.proxy_model.mapToSource(index)
        file_path = self.source_model.filePath(source_index)
        if os.path.isfile(file_path):
            rel_path = os.path.relpath(file_path, self.temp_dir)
            size = self.size_map.get(file_path, 0)
            size_str = self.source_model.format_size(size)
            QMessageBox.information(
                self, 
                "File Selected", 
                f"OCI Object Path: {rel_path}\nSize: {size_str}"
            )