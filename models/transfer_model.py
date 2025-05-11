from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class TransferItem:
    """Class representing a transfer item in the queue"""
    def __init__(self, source, destination, type, size=0):
        self.source = source
        self.destination = destination
        self.type = type  # 'upload' or 'download'
        self.size = size
        self.status = 'pending'  # 'pending', 'in_progress', 'completed', 'failed'
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.error = None
    
    def to_dict(self):
        return {
            'source': self.source,
            'destination': self.destination,
            'type': self.type,
            'size': self.size,
            'status': self.status,
            'progress': self.progress,
            'start_time': str(self.start_time) if self.start_time else None,
            'end_time': str(self.end_time) if self.end_time else None,
            'error': self.error
        }

class TransferModel(QObject):
    """Model for managing transfer queue"""
    transfer_added = pyqtSignal(int)
    transfer_updated = pyqtSignal(int)
    transfer_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.transfer_queue = []
        self.current_worker = None
    
    def add_transfer(self, transfer_item):
        """Add a new transfer to the queue"""
        self.transfer_queue.append(transfer_item)
        self.transfer_added.emit(len(self.transfer_queue) - 1)
    
    def update_transfer(self, index, **kwargs):
        """Update transfer item properties"""
        for key, value in kwargs.items():
            setattr(self.transfer_queue[index], key, value)
        self.transfer_updated.emit(index)
    
    def clear_completed(self):
        """Remove completed transfers from queue"""
        self.transfer_queue = [item for item in self.transfer_queue 
                             if item.status != 'completed']
    
    def get_transfer(self, index):
        """Get transfer item by index"""
        return self.transfer_queue[index]
    
    def get_all_transfers(self):
        """Get all transfer items"""
        return self.transfer_queue