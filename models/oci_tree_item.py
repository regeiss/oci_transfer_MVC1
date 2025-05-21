# 
class OCITreeItem:
    def __init__(self, name, is_folder=False, size=None, modified=None, storage_tier=None, parent=None, full_name=None):
        self.name = name
        self.is_folder = is_folder
        self.size = size
        self.modified = modified
        self.storage_tier = storage_tier
        self.parent_item = parent
        self.children = []
        self.full_name = full_name
        
    def appendChild(self, child):
        self.children.append(child)

    def child(self, row):
        return self.children[row] if 0 <= row < len(self.children) else None

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return 4  # Name, Size, Modified, Tier

    def data(self, column):
        if column == 0:
            return self.name
        elif column == 1:
            return self.size
        elif column == 2:
            return self.modified
        elif column == 3:
            return "Padrão" if self.storage_tier is None else self.storage_tier
        return None

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.children.index(self)
        return 0