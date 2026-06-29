from PIL import ImageGrab
import pytesseract
from config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def get_clipboard_text() -> str:
    screenshot = ImageGrab.grabclipboard()
    
    if screenshot is None:
        raise ValueError("Clipboard empty or no image found.")

    config_ocr = "--psm 6"
    text = pytesseract.image_to_string(screenshot, lang="ell", config=config_ocr).strip()

    clean_text = " ".join(text.split())
    return clean_text