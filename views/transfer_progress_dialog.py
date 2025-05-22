from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton, QHBoxLayout

class TransferProgressDialog(QDialog):
    def __init__(self, total_files, qapp, parent=None):
        super().__init__(parent)
        self.qapp = qapp
        self.setWindowTitle("Transferência de Arquivos")
        self.setMinimumWidth(400)
        self.cancelled = False
        self.paused = False

        layout = QVBoxLayout(self)
        self.label = QLabel("Iniciando transferência...")
        layout.addWidget(self.label)

        # Progress bar for current file
        self.file_progress_bar = QProgressBar()
        self.file_progress_bar.setMaximum(100)
        self.file_progress_bar.setValue(0)
        layout.addWidget(self.file_progress_bar)

        # Label for total progress bar
        self.total_label = QLabel("Progresso total dos arquivos:")
        layout.addWidget(self.total_label)

        # Progress bar for total files
        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setMaximum(total_files)
        self.total_progress_bar.setValue(0)
        layout.addWidget(self.total_progress_bar)

        btn_layout = QHBoxLayout()
        self.pause_btn = QPushButton("Pausar")
        self.resume_btn = QPushButton("Retomar")
        self.cancel_btn = QPushButton("Cancelar")
        btn_layout.addStretch()
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.pause_btn.clicked.connect(self.pause_transfer)
        self.resume_btn.clicked.connect(self.resume_transfer)
        self.cancel_btn.clicked.connect(self.cancel_transfer)
        self.resume_btn.setEnabled(False)

    def update_file_progress(self, percent):
        self.file_progress_bar.setValue(percent)
        self.qapp.processEvents()

    def update_total_progress(self, current, total, filename):
        self.label.setText(f"Baixando: {filename} ({current}/{total})")
        self.total_progress_bar.setValue(current)
        self.qapp.processEvents()

    def pause_transfer(self):
        self.paused = True
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(True)

    def resume_transfer(self):
        self.paused = False
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)

    def cancel_transfer(self):
        self.cancelled = True