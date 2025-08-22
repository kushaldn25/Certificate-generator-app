# app.py
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QSpinBox,
    QScrollArea
)
from PyQt5.QtCore import Qt
from PIL import Image, ImageFont
from config import FONT_CHOICES, DEFAULT_FONT_SIZE
from utils import find_font_path, pick_name_column, draw_centered_text, image_to_qpixmap
from dialogs import ImagePreviewDialog

class CertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Certificate Generator")
        self.resize(900,650)

        # State variables
        self.template_img, self.df, self.name_col, self.current_pixmap = None,None,None,None
        self.excel_path = ""

        # Build UI
        self._build_ui()

    # -------- UI SETUP --------
    def _build_ui(self):
        self.excel_edit, self.excel_btn = QLineEdit(), QPushButton("Browse Excel")
        self.excel_btn.clicked.connect(self.load_excel)
        self.template_edit, self.template_btn = QLineEdit(), QPushButton("Browse Template")
        self.template_btn.clicked.connect(self.load_template)

        self.font_combo, self.font_size = QComboBox(), QSpinBox()
        self.font_combo.addItems(FONT_CHOICES.keys())
        self.font_size.setRange(10,300); self.font_size.setValue(DEFAULT_FONT_SIZE)
        self.center_x, self.center_y = QSpinBox(), QSpinBox()
        for sp in (self.center_x,self.center_y): sp.setRange(0,10000)
        self.center_x.setValue(650); self.center_y.setValue(460)

        self.preview_label = QLabel("Preview will appear here",alignment=Qt.AlignCenter)
        self.preview_label.setStyleSheet("QLabel{background:#f4f4f4;border:1px solid #ddd;}")
        self.preview_label.setMinimumHeight(400)
        self.preview_label.mouseDoubleClickEvent = self.show_full_preview

        self.preview_btn, self.gen_btn = QPushButton("Preview"), QPushButton("Generate PDFs")
        self.preview_btn.clicked.connect(self.preview)
        self.gen_btn.clicked.connect(self.generate)

        # Layout
        top = QVBoxLayout()
        top.addLayout(self._hrow("Excel:", self.excel_edit, self.excel_btn))
        top.addLayout(self._hrow("Template:", self.template_edit, self.template_btn))
        top.addLayout(self._hrow("Font:", self.font_combo, "Size:", self.font_size,
                                "X:", self.center_x, "Y:", self.center_y))
        top.addLayout(self._hrow(self.preview_btn, self.gen_btn))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(self.preview_label)
        top.addWidget(scroll,1)
        self.setLayout(top)

    def _hrow(self,*widgets):
        l = QHBoxLayout()
        for w in widgets:
            l.addWidget(QLabel(w) if isinstance(w,str) else w, 1 if isinstance(w,QLineEdit) else 0)
        return l

    # -------- CORE FUNCTIONS --------
    def load_excel(self):
        path,_ = QFileDialog.getOpenFileName(self,"Select Excel","","Excel Files (*.xlsx)")
        if path:
            try:
                self.df = pd.read_excel(path,engine="openpyxl")
                self.name_col = pick_name_column(self.df)
                self.excel_edit.setText(path); self.excel_path = path
                QMessageBox.information(self,"Excel Loaded",
                    f"Columns: {list(self.df.columns)}\nUsing: {self.name_col}")
            except Exception as e: QMessageBox.critical(self,"Excel Error",str(e))

    def load_template(self):
        path,_ = QFileDialog.getOpenFileName(self,"Select Template","","Images (*.jpg *.png)")
        if path:
            try:
                from PIL import Image
                self.template_img = Image.open(path).convert("RGB")
                w,h = self.template_img.size
                self.center_x.setValue(w//2); self.center_y.setValue(h//2)
                self.template_edit.setText(path)
                self.show_preview("Sample Name")
            except Exception as e: QMessageBox.critical(self,"Template Error",str(e))

    def build_font(self):
        font_file = FONT_CHOICES[self.font_combo.currentText()]
        return ImageFont.truetype(find_font_path(font_file), self.font_size.value())

    # -------- PREVIEW --------
    def show_preview(self,text):
        if not self.template_img: return
        img = self.template_img.copy()
        draw_centered_text(img,text,(self.center_x.value(),self.center_y.value()),self.build_font())
        self.current_pixmap = image_to_qpixmap(img)
        self.preview_label.setPixmap(self.current_pixmap.scaled(
            self.preview_label.width(),self.preview_label.height(),
            Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def preview(self):
        text="Sample Name"
        if self.df is not None and len(self.df)>0: 
            text = str(self.df.iloc[0][self.name_col]).strip() or text
        self.show_preview(text)

    def show_full_preview(self,event):
        if self.current_pixmap: ImagePreviewDialog(self.current_pixmap,self).exec_()

    # -------- GENERATION --------
    def generate(self):
        if not self.template_img or self.df is None:
            return QMessageBox.warning(self,"Missing","Load Excel and Template first.")
        outdir = os.path.join(os.path.dirname(self.excel_path),"certificates")
        os.makedirs(outdir,exist_ok=True)
        font = self.build_font(); count=0
        for _,row in self.df.iterrows():
            name = str(row[self.name_col]).strip()
            if not name: continue
            img=self.template_img.copy()
            draw_centered_text(img,name,(self.center_x.value(),self.center_y.value()),font)
            img.save(os.path.join(outdir,f"{name}.pdf"),"PDF"); count+=1
        QMessageBox.information(self,"Done",f"Generated {count} PDF(s) in {outdir}")
