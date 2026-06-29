import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

URL_BACKEND = os.getenv("URL_BACKEND")
SHORTCUT_KEY = os.getenv("SHORTCUT_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

