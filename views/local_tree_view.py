from PyQt5.QtWidgets import QTreeView, QHeaderView
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