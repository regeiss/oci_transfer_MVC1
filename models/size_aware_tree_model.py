from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileSystemModel

class SizeAwareFileSystemModel(QFileSystemModel):
    def __init__(self, size_map, parent=None):
        super().__init__(parent)
        self.size_map = size_map
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == 1:  # Size column
            file_path = self.filePath(index)
            if file_path in self.size_map:
                return self.format_size(self.size_map[file_path])
        return super().data(index, role)
    
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"     