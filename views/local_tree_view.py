from PyQt5.QtWidgets import QTreeView, QHeaderView, QMessageBox
from PyQt5.QtCore import QMimeData, Qt, QUrl
from PyQt5.QtGui import QDrag
from models.local_file_model import LocalFileModel
from views.custom_header_tree_view import CustomHeaderTreeView
import os

class LocalTreeView(CustomHeaderTreeView):
    """View for local file system with custom headers"""
    def __init__(self, viewmodel=None, parent=None):
        super().__init__()
        self.setModel(LocalFileModel())
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeView.DragDrop)
        self.setContextMenuPolicy(Qt.CustomContextMenu) 
        self._viewmodel = viewmodel
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
            QMessageBox.warning(None, "Erro", "Nenhum arquivo selecionado no Local Tree View.")
            return

        return selected_files

    def get_selected_directory(self):
        """Get the currently selected directory in the Local Tree View."""
        selected_indexes = self.selectionModel().selectedIndexes()

        if not selected_indexes:
            QMessageBox.warning(None, "Erro", "Nenhum diretório selecionado no Local Tree View.")
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

    def startDrag(self, supportedActions):
        indexes = self.selectedIndexes()
        if not indexes:
            return
        mime_data = QMimeData()
        urls = []
        for index in indexes:
            if index.column() == 0:  # Only process the first column
                file_path = self.model().filePath(index)
                urls.append(QUrl.fromLocalFile(file_path))
        mime_data.setUrls(urls)
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-oci-object"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-oci-object"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-oci-object"):
            object_names = event.mimeData().data("application/x-oci-object").data().decode("utf-8").split(";")
            # Determine the local directory where the drop happened
            index = self.indexAt(event.pos())
            if index.isValid():
                local_directory = self.model().filePath(index)
                if not os.path.isdir(local_directory):
                    local_directory = os.path.dirname(local_directory)
            else:
                local_directory = self.model().rootPath()
            # Get the selected bucket from the viewmodel (adjust as needed)
            bucket_name = self._viewmodel.get_selected_bucket()
            # Call the viewmodel to perform the download
            self._viewmodel.copy_to_local(object_names, bucket_name, local_directory)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)