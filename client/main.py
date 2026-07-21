import tkinter as tk
import keyboard
from config import SHORTCUT_KEY
from ui.overlay import ProstagmaOverlay

if __name__ == "__main__":
    print("Initializing Prostagma Client...")
    
    root = tk.Tk()
    overlay = ProstagmaOverlay(root, SHORTCUT_KEY)
    
    root.mainloop()