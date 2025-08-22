# utils.py
import os, glob
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QPixmap
import pandas as pd
from config import GOLDEN, NAME_COLUMN_CANDIDATES

def find_font_path(font_filename: str) -> str:
    """Locate font file from system directories."""
    if os.path.exists(font_filename): 
        return os.path.abspath(font_filename)
    search_dirs = [
        ".", "fonts", "C:/Windows/Fonts", 
        "/usr/share/fonts", "/usr/local/share/fonts",
        "/Library/Fonts", "/System/Library/Fonts"
    ]
    for d in search_dirs:
        for f in glob.glob(os.path.join(d, "**", "*.*"), recursive=True):
            if font_filename.split(".")[0].lower() in os.path.basename(f).lower():
                return f
    return font_filename

def pick_name_column(df: pd.DataFrame) -> str:
    """Find the most likely column containing names."""
    for cand in NAME_COLUMN_CANDIDATES:
        if cand in df.columns: return cand
    for c in df.columns:
        if df[c].dtype == "object": return c
    raise ValueError("No suitable name column found.")

def draw_centered_text(img, text, center_xy, font, color=GOLDEN):
    """Draw text centered at given coordinates."""
    d = ImageDraw.Draw(img)
    w,h = d.textbbox((0,0), text, font=font)[2:]
    x,y = center_xy[0]-w/2, center_xy[1]-h/2
    d.text((x,y), text, font=font, fill=color)

def image_to_qpixmap(img: Image.Image) -> QPixmap:
    """Convert Pillow image to QPixmap."""
    buf = BytesIO(); img.save(buf, format="PNG")
    pix = QPixmap(); pix.loadFromData(buf.getvalue())
    return pix
