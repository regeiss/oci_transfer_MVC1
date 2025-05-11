from PyQt5.QtWidgets import QTreeView, QHeaderView
from PyQt5.QtCore import Qt

class CustomHeaderTreeView(QTreeView):
    """Base class for tree views with customizable headers"""
    def __init__(self):
        super().__init__()
        self._header_labels = []
        self._header_sizes = []
        self._header_resize_modes = []
        
        # Configure header
        header = self.header()
        header.setSectionsClickable(True)
        header.setStretchLastSection(False)
    
    def set_header_labels(self, labels):
        """Set custom header labels"""
        self._header_labels = labels
        model = self.model()
        if model:
            for i, label in enumerate(labels):
                if i < model.columnCount():
                    model.setHeaderData(i, Qt.Horizontal, label)
    
    def set_header_sizes(self, sizes):
        """Set initial header sizes"""
        self._header_sizes = sizes
        header = self.header()
        for i, size in enumerate(sizes):
            if i < header.count():
                header.resizeSection(i, size)
    
    def set_header_resize_modes(self, modes):
        """Set how columns resize"""
        self._header_resize_modes = modes
        header = self.header()
        for i, mode in enumerate(modes):
            if i < header.count():
                header.setSectionResizeMode(i, mode)
    
    def setModel(self, model):
        """Override setModel to apply header settings"""
        super().setModel(model)
        if model:
            # Apply header settings to the new model
            for i, label in enumerate(self._header_labels):
                if i < model.columnCount():
                    model.setHeaderData(i, Qt.Horizontal, label)
            
            # Configure header behavior
            header = self.header()
            for i, size in enumerate(self._header_sizes):
                if i < header.count():
                    header.resizeSection(i, size)
            for i, mode in enumerate(self._header_resize_modes):
                if i < header.count():
                    header.setSectionResizeMode(i, mode)