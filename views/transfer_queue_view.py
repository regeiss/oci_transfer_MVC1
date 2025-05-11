from PyQt5.QtWidgets import QTabWidget, QListWidget, QLabel, QVBoxLayout, QWidget

class TransferQueueView(QTabWidget):
    """View for displaying transfer queue with a tabbed layout"""
    def __init__(self):
        super().__init__()

        # Tab 1: Transfer Queue List
        self.queue_list = QListWidget()
        self.queue_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.addTab(self.queue_list, "Fila de Transferência")

        # Tab 2: Transfer Summary
        self.summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        summary_label = QLabel("Sumário da Transferência")
        summary_layout.addWidget(summary_label)
        self.summary_widget.setLayout(summary_layout)
        self.addTab(self.summary_widget, "Sumário da Transferência")

        # Tab 3: Transfer Details
        self.details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_label = QLabel("Histórico de Transferências")
        details_layout.addWidget(details_label)
        self.details_widget.setLayout(details_layout)
        self.addTab(self.details_widget, "Histórico de Transferências")