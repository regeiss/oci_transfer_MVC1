from PyQt5.QtWidgets import QTreeView, QHeaderView
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

        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.adjust_column_widths()
        self.model().modelReset.connect(self.adjust_column_widths)
        
    def adjust_column_widths(self):
        """Resize columns to fit their content"""
        for column in range(self.model().columnCount()):
            self.resizeColumnToContents(column)    

    