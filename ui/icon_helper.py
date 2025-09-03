
from PIL import Image, ImageTk
import os

def load_icon(filename, size=(30,30)):
    path = os.path.join(os.path.dirname(__file__), "icons", filename)
    try:
        img = Image.open(path)
        img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Icon loading error for {filename}: {e}")
        return None
