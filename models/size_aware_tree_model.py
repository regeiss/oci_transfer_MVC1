import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileSystemModel

class SizeAwareFileSystemModel(QFileSystemModel):
    def __init__(self, size_map, parent=None):
        super().__init__(parent)
        self.size_map = size_map
        self.date_map = {}  # Add this line

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if index.column() == 1:  # Size column
                file_path = os.path.abspath(self.filePath(index))
                if file_path in self.size_map:
                    return self.format_size(self.size_map[file_path])
            elif index.column() == 3:  # Date Modified column
                file_path = os.path.abspath(self.filePath(index))
                if hasattr(self, "date_map") and file_path in self.date_map:
                    dt = self.date_map[file_path]
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
        return super().data(index, role)

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"