from PyQt5.QtWidgets import QTreeView, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from models.oci_tree_model import OciTreeModel
from views.custom_header_tree_view import CustomHeaderTreeView

class OciTreeView(QTreeView):
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
        self.set_header_resize_modes([
            QHeaderView.Stretch,
            QHeaderView.ResizeToContents,
            QHeaderView.ResizeToContents,
            QHeaderView.Interactive
        ])
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.adjust_column_widths()
        self.model().modelReset.connect(self.adjust_column_widths)
        
    def set_header_resize_modes(self, modes):
        """Set how columns resize"""
        self._header_resize_modes = modes
        header = self.header()
        for i, mode in enumerate(modes):
            if i < header.count():
                header.setSectionResizeMode(i, mode)

    def adjust_column_widths(self):
        """Resize columns to fit their content"""
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)    

    def get_selected_to_local(self):
        """Get the list of files selected in the OCI tree."""
        selected_indexes = self.selectionModel().selectedIndexes()

        # Extract file paths from the selected indexes
        selected_files = []
        for index in selected_indexes:
            if index.column() == 0:  # Only process the first column (file name)
                item = index.internalPointer()
                if not item.is_folder:  # Only include files
                    selected_files.append(item.full_name)

        if not selected_files:
            QMessageBox.warning(None, "Erro", "Nenhum arquivo selecionado no Oci Tree View.")
            return

        return selected_files

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events to open folders"""
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        item = index.internalPointer()
        if item.is_folder:  # Check if the item is a folder
            # Update the model to load the contents of the selected folder
            self.model().load_bucket_objects(item.name)
        else:
            print(f"Double-clicked on file: {item.name}")

        super().mouseDoubleClickEvent(event)