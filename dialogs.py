# dialogs.py
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class ImagePreviewDialog(QDialog):
    """Fullscreen preview for certificate image."""
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Screen Preview")
        lbl = QLabel()
        lbl.setPixmap(pixmap.scaledToWidth(1200, Qt.SmoothTransformation))
        lay = QVBoxLayout(self); lay.addWidget(lbl)
        self.resize(1280,720)
