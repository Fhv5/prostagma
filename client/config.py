import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = Path(sys.executable).parent
    else:
        # Running as a script
        base_dir = Path(__file__).resolve().parent

    env_path = base_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

URL_BACKEND = os.getenv("URL_BACKEND")
SHORTCUT_KEY = os.getenv("SHORTCUT_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

def save_config(url_backend, shortcut_key, tesseract_cmd):
    global URL_BACKEND, SHORTCUT_KEY, TESSERACT_CMD
    URL_BACKEND = url_backend
    SHORTCUT_KEY = shortcut_key
    TESSERACT_CMD = tesseract_cmd

    try:
        from dotenv import set_key
        # Ensure the .env file exists before setting keys
        if not env_path.exists():
            env_path.touch()
        
        set_key(str(env_path), "URL_BACKEND", url_backend)
        set_key(str(env_path), "SHORTCUT_KEY", shortcut_key)
        set_key(str(env_path), "TESSERACT_CMD", tesseract_cmd)
    except ImportError:
        pass

