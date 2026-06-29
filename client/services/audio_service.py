import io
import threading
from gtts import gTTS
import pygame

pygame.mixer.init()

def _play_audio_async(text: str, lang: str = 'el', slow: bool = False):
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except Exception as e:
        print(f"[Audio Error] Could not play audio: {e}")

def play_pronunciation(text: str, slow: bool = False):
    if not text:
        return
    threading.Thread(target=_play_audio_async, args=(text, 'el', slow), daemon=True).start()