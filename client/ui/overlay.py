import tkinter as tk
import queue
import threading
import keyboard
import config
from services.ocr_service import get_clipboard_text, set_tesseract_cmd
from services.api_service import send_for_translation
from services.audio_service import play_pronunciation

class ProstagmaOverlay:
    def __init__(self, root, shortcut_key):
        self.root = root
        self.shortcut_key = shortcut_key
        keyboard.add_hotkey(self.shortcut_key, self.trigger_translation)
        self.message_queue = queue.Queue()
        
        # --- UI STATES ---
        self.is_collapsed = False
        self.is_minimal = False
        
        # --- DYNAMIC DIMENSIONS ---
        self.width = 800
        self.height_detailed = 250 
        self.height_minimal = 100
        self.height_collapsed = 24
        
        # --- IN-MEMORY DATA ---
        self.greek_text = ""
        self.literal_text = ""
        self.interpreted_text = ""
        self.google_text = ""
        self.current_state = f"Ready. Use Win+Shift+S and then {self.shortcut_key.upper()}"
        self.has_error = False
        self.current_color = "#ffffff"
        
        self._setup_ui()
        self.root.after(100, self._process_queue)

    def _setup_ui(self):
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)
        self.root.configure(bg='#111111')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (self.width / 2))
        y = int(screen_height - self.height_detailed - 50)
        self.root.geometry(f"{self.width}x{self.height_detailed}+{x}+{y}")

        # --- 1. TOP BAR (DRAG ZONE) ---
        self.header = tk.Frame(self.root, bg='#222222', height=self.height_collapsed, cursor="fleur")
        self.header.pack(fill='x', side='top')
        self.header.pack_propagate(False)
        
        # EXCLUSIVE bindings on the header to move the window
        self.header.bind("<Button-1>", self._start_drag)
        self.header.bind("<B1-Motion>", self._on_drag)

        self.title_label = tk.Label(self.header, text="Prostagma?", bg='#222222', fg='#aaaaaa', font=('Helvetica', 9))
        self.title_label.pack(side='left', padx=10)
        # Bindings on the title label as well
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)

        self.btn_collapse = tk.Button(
            self.header, text="—", bg='#222222', fg='#ffffff', bd=0, 
            activebackground='#444444', activeforeground='#ffffff', command=self._toggle_collapse, cursor="hand2"
        )
        self.btn_collapse.pack(side='right', padx=5)

        self.btn_settings = tk.Button(
            self.header, text="⚙️", bg='#222222', fg='#ffffff', bd=0, 
            activebackground='#444444', activeforeground='#ffffff', command=self._open_settings, cursor="hand2"
        )
        self.btn_settings.pack(side='right', padx=5)

        self.btn_view = tk.Button(
            self.header, text="↕️", bg='#222222', fg='#ffffff', bd=0, 
            activebackground='#444444', activeforeground='#ffffff', command=self._toggle_view, cursor="hand2"
        )
        self.btn_view.pack(side='right', padx=5)

        # --- 2. MAIN CONTENT ---
        self.content_frame = tk.Frame(self.root, bg='#111111')
        self.content_frame.pack(expand=True, fill='both', padx=10, pady=(0, 5))

        # Audio Panel
        self.audio_frame = tk.Frame(self.content_frame, bg='#111111')
        self.audio_frame.pack(side='right', fill='y', padx=5, pady=5)

        self.btn_audio = tk.Button(
            self.audio_frame, text="🔊", bg='#222222', fg='#ffffff', bd=0,
            activebackground='#444444', font=('Helvetica', 14),
            command=lambda: self._play_audio(False), cursor="hand2", state="disabled"
        )
        self.btn_audio.pack(side='top', pady=(0, 2), fill='x', expand=True)

        self.btn_audio_slow = tk.Button(
            self.audio_frame, text="🐢", bg='#222222', fg='#ffffff', bd=0,
            activebackground='#444444', font=('Helvetica', 14),
            command=lambda: self._play_audio(True), cursor="hand2", state="disabled"
        )
        self.btn_audio_slow.pack(side='top', pady=(2, 0), fill='x', expand=True)

        # TEXT AREA
        self.label = tk.Text(
            self.content_frame, font=('Helvetica', 14, 'bold'), fg='#ffffff', bg='#111111',
            bd=0, relief="flat", wrap="word", selectbackground="#445566", selectforeground="#ffffff",
            cursor="xterm" 
        )
        self.label.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        self.label.tag_configure("center", justify="center")
        
        self._write_locked_text(self.current_state, "#ffffff")

    # --- DRAG LOGIC ---
    def _start_drag(self, event):
        # Triggers only when clicking on the header
        self.x_offset = event.x
        self.y_offset = event.y

    def _on_drag(self, event):
        # Moves only when dragged from the header
        x = self.root.winfo_x() + event.x - self.x_offset
        y = self.root.winfo_y() + event.y - self.y_offset
        self.root.geometry(f"+{x}+{y}")

    # --- VIEW TOGGLE ---
    def _toggle_view(self):
        self.is_minimal = not self.is_minimal
        self._render_text()
        
        if not self.is_collapsed:
            target_height = self.height_minimal if self.is_minimal else self.height_detailed
            self.root.geometry(f"{self.width}x{target_height}")

    # --- SETTINGS MODAL ---
    def _open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Prostagma Settings")
        settings_win.geometry("450x250")
        settings_win.configure(bg='#222222')
        settings_win.attributes('-topmost', True)

        tk.Label(settings_win, text="Backend URL:", bg='#222222', fg='#ffffff').pack(anchor='w', padx=10, pady=(10, 0))
        url_var = tk.StringVar(value=config.URL_BACKEND)
        tk.Entry(settings_win, textvariable=url_var, width=50).pack(padx=10, pady=2)

        tk.Label(settings_win, text="Shortcut Key (e.g., ctrl+shift+a):", bg='#222222', fg='#ffffff').pack(anchor='w', padx=10, pady=(10, 0))
        shortcut_var = tk.StringVar(value=config.SHORTCUT_KEY)
        tk.Entry(settings_win, textvariable=shortcut_var, width=50).pack(padx=10, pady=2)

        tk.Label(settings_win, text="Tesseract OCR Path:", bg='#222222', fg='#ffffff').pack(anchor='w', padx=10, pady=(10, 0))
        tesseract_var = tk.StringVar(value=config.TESSERACT_CMD)
        tk.Entry(settings_win, textvariable=tesseract_var, width=50).pack(padx=10, pady=2)

        def save_and_close():
            new_url = url_var.get().strip()
            new_shortcut = shortcut_var.get().strip()
            new_tesseract = tesseract_var.get().strip()

            config.save_config(new_url, new_shortcut, new_tesseract)
            set_tesseract_cmd(new_tesseract)
            
            # Rebind hotkey
            try:
                keyboard.remove_hotkey(self.shortcut_key)
            except Exception:
                pass
            
            self.shortcut_key = new_shortcut
            try:
                keyboard.add_hotkey(self.shortcut_key, self.trigger_translation)
                self.current_state = f"Ready. Use Win+Shift+S and then {self.shortcut_key.upper()}"
                self._render_text()
            except Exception as e:
                self.message_queue.put(("error", f"Failed to bind hotkey: {e}"))
                
            settings_win.destroy()

        tk.Button(settings_win, text="Save", command=save_and_close, bg='#44aa44', fg='#ffffff', width=15).pack(pady=20)


    # --- COLLAPSE LOGIC ---
    def _toggle_collapse(self, force_expand=False):
        if self.is_collapsed or force_expand:
            if not self.is_collapsed and force_expand:
                return
            
            target_height = self.height_minimal if self.is_minimal else self.height_detailed
            self.root.geometry(f"{self.width}x{target_height}")
            self.content_frame.pack(expand=True, fill='both', padx=10, pady=(0, 5))
            self.btn_collapse.config(text="—")
            self.is_collapsed = False
        else:
            self.content_frame.pack_forget()
            self.root.geometry(f"{self.width}x{self.height_collapsed}")
            self.btn_collapse.config(text="□")
            self.is_collapsed = True

    # --- AUDIO EVENTS ---
    def _play_audio(self, slow):
        if self.greek_text:
            play_pronunciation(self.greek_text, slow)

    # --- SAFE TEXT WRITING ---
    def _write_locked_text(self, content, font_color):
        self.label.config(state="normal", fg=font_color)
        self.label.delete("1.0", tk.END)
        self.label.insert(tk.END, content, "center")
        self.label.config(state="disabled")

    # --- UI UPDATING ---
    def _render_text(self):
        if self.has_error or not self.greek_text:
            self.label.config(font=('Helvetica', 14, 'bold'))
            self._write_locked_text(self.current_state, self.current_color)
            return

        if self.is_minimal:
            self.label.config(font=('Helvetica', 16, 'bold'))
            self._write_locked_text(f"Translation: {self.interpreted_text}", "#55ff55")
        else:
            self.label.config(font=('Helvetica', 12, 'bold'))
            text = f"Original: {self.greek_text}\n\n"
            text += f"Translation: {self.interpreted_text}\n"
            text += f"Literal: {self.literal_text}\n"
            text += f"Google: {self.google_text}"
            self._write_locked_text(text, "#55ff55")

    def _update_ui(self, message_type, payload):
        if message_type == "error":
            self.has_error = True
            self.current_state = payload
            self.current_color = "#ff5555"
            self.btn_audio.config(state="disabled", bg='#222222')
            self.btn_audio_slow.config(state="disabled", bg='#222222')
        elif message_type == "state":
            self.has_error = True 
            self.current_state = payload
            self.current_color = "#aaaaaa"
            self.btn_audio.config(state="disabled", bg='#222222')
            self.btn_audio_slow.config(state="disabled", bg='#222222')
        elif message_type == "success":
            self.has_error = False
            self.greek_text = payload["greek"]
            self.literal_text = payload["literal"]
            self.interpreted_text = payload["interpreted"]
            self.google_text = payload["google"]
            self.btn_audio.config(state="normal", bg='#1a4a1a')
            self.btn_audio_slow.config(state="normal", bg='#1a4a1a')
            
        self._render_text()

    def _process_queue(self):
        while not self.message_queue.empty():
            message_type, payload = self.message_queue.get()
            self._update_ui(message_type, payload)
            
            if message_type in ["success", "error"]:
                self._toggle_collapse(force_expand=True)
                
        self.root.after(100, self._process_queue)

    # --- ASYNC FLOW ---
    def _execute_async_flow(self):
        self.message_queue.put(("state", "Capturing..."))
        try:
            greek_text = get_clipboard_text()
            if not greek_text:
                self.message_queue.put(("error", "OCR did not detect any text."))
                return
                
            self.message_queue.put(("state", "Analyzing..."))
            data = send_for_translation(greek_text)
            
            self.message_queue.put(("success", {
                "greek": greek_text,
                "literal": data.get('literal', 'N/A'),
                "interpreted": data.get('interpreted', 'N/A'),
                "google": data.get('google', 'N/A')
            }))
            
        except ValueError as e:
            self.message_queue.put(("error", str(e)))
        except Exception as e:
            self.message_queue.put(("error", f"Error: {str(e)}"))

    def trigger_translation(self):
        threading.Thread(target=self._execute_async_flow, daemon=True).start()