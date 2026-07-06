import tkinter as tk
from tkinter import ttk
import threading
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyperclip
import os
import tempfile


class TranslationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translation Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")
        self.root.minsize(800, 600)

        self.languages = {
            "Auto Detect": "auto",
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese (Simplified)": "zh-CN",
            "Arabic": "ar",
            "Hindi": "hi",
            "Dutch": "nl",
            "Swedish": "sv",
            "Polish": "pl",
            "Turkish": "tr",
            "Vietnamese": "vi",
            "Thai": "th",
            "Ukrainian": "uk",
            "Indonesian": "id",
            "Malay": "ms"
        }

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_frame, bg="#667eea")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="Language Translation Tool",
            font=("Helvetica", 24, "bold"),
            bg="#667eea",
            fg="white"
        )
        title_label.pack(pady=15)

        subtitle_label = tk.Label(
            header_frame,
            text="Translate text between multiple languages",
            font=("Helvetica", 12),
            bg="#667eea",
            fg="#e0e0e0"
        )
        subtitle_label.pack(pady=(0, 15))

        lang_frame = tk.Frame(main_frame, bg="#f0f2f5")
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        source_frame = tk.LabelFrame(lang_frame, text="From", bg="#f0f2f5", font=("Helvetica", 10, "bold"))
        source_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.source_lang = ttk.Combobox(
            source_frame,
            values=list(self.languages.keys()),
            state="readonly",
            font=("Helvetica", 11)
        )
        self.source_lang.set("Auto Detect")
        self.source_lang.pack(padx=10, pady=10, fill=tk.X)

        swap_btn = tk.Button(
            lang_frame,
            text="⇄",
            font=("Helvetica", 16),
            bg="#667eea",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.swap_languages,
            width=4
        )
        swap_btn.pack(side=tk.LEFT, padx=10)

        target_frame = tk.LabelFrame(lang_frame, text="To", bg="#f0f2f5", font=("Helvetica", 10, "bold"))
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.target_lang = ttk.Combobox(
            target_frame,
            values=[lang for lang in list(self.languages.keys()) if lang != "Auto Detect"],
            state="readonly",
            font=("Helvetica", 11)
        )
        self.target_lang.set("Spanish")
        self.target_lang.pack(padx=10, pady=10, fill=tk.X)

        text_frame = tk.Frame(main_frame, bg="#f0f2f5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)

        input_frame = tk.LabelFrame(text_frame, text="Input Text", bg="#f0f2f5", font=("Helvetica", 10, "bold"))
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.input_text = tk.Text(
            input_frame,
            height=10,
            font=("Helvetica", 12),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="white"
        )
        self.input_text.pack(padx=10, pady=(5, 0), fill=tk.BOTH, expand=True)

        input_btn_frame = tk.Frame(input_frame, bg="#f0f2f5")
        input_btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.char_count = tk.Label(
            input_btn_frame,
            text="0 / 5000",
            font=("Helvetica", 9),
            bg="#f0f2f5",
            fg="#666"
        )
        self.char_count.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            input_btn_frame,
            text="Clear",
            font=("Helvetica", 9),
            bg="#e0e0e0",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_input
        )
        clear_btn.pack(side=tk.RIGHT)

        self.input_text.bind("<KeyRelease>", self.update_char_count)

        output_frame = tk.LabelFrame(text_frame, text="Translation", bg="#f0f2f5", font=("Helvetica", 10, "bold"))
        output_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.output_text = tk.Text(
            output_frame,
            height=10,
            font=("Helvetica", 12),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="white",
            state=tk.DISABLED
        )
        self.output_text.pack(padx=10, pady=(5, 0), fill=tk.BOTH, expand=True)

        output_btn_frame = tk.Frame(output_frame, bg="#f0f2f5")
        output_btn_frame.pack(fill=tk.X, padx=10, pady=5)

        copy_btn = tk.Button(
            output_btn_frame,
            text="Copy",
            font=("Helvetica", 9),
            bg="#28a745",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.copy_translation
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.speak_btn = tk.Button(
            output_btn_frame,
            text="🔊 Speak",
            font=("Helvetica", 9),
            bg="#17a2b8",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.speak_translation
        )
        self.speak_btn.pack(side=tk.LEFT)

        btn_frame = tk.Frame(main_frame, bg="#f0f2f5")
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.translate_btn = tk.Button(
            btn_frame,
            text="Translate",
            font=("Helvetica", 14, "bold"),
            bg="#667eea",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.translate_text,
            height=2
        )
        self.translate_btn.pack(fill=tk.X)

        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 10),
            bg="#f0f2f5"
        )
        self.status_label.pack(fill=tk.X)

        footer_frame = tk.Frame(main_frame, bg="#e0e0e0")
        footer_frame.pack(fill=tk.X, pady=(20, 0))

        footer_label = tk.Label(
            footer_frame,
            text="Powered by Google Translate API",
            font=("Helvetica", 9),
            bg="#e0e0e0",
            fg="#666"
        )
        footer_label.pack(pady=10)

    def update_char_count(self, event=None):
        count = len(self.input_text.get("1.0", tk.END).strip())
        self.char_count.config(text=f"{count} / 5000")

    def show_status(self, message, msg_type="info"):
        colors = {
            "info": "#333",
            "error": "#d32f2f",
            "success": "#2e7d32",
            "loading": "#f57c00"
        }
        self.status_label.config(text=message, fg=colors.get(msg_type, "#333"))
        if msg_type != "loading":
            self.root.after(5000, lambda: self.status_label.config(text=""))

    def clear_input(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", "Translation will appear here...")
        self.output_text.config(state=tk.DISABLED)
        self.update_char_count()
        self.status_label.config(text="")

    def swap_languages(self):
        source = self.source_lang.get()
        if source == "Auto Detect":
            self.show_status("Cannot swap when source is set to Auto Detect", "error")
            return

        target = self.target_lang.get()
        self.source_lang.set(target)
        self.target_lang.set(source)

        input_content = self.input_text.get("1.0", tk.END).strip()
        output_content = self.output_text.get("1.0", tk.END).strip()

        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", output_content)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", input_content)
        self.output_text.config(state=tk.DISABLED)

        self.update_char_count()

    def translate_text(self):
        text = self.input_text.get("1.0", tk.END).strip()

        if not text:
            self.show_status("Please enter text to translate", "error")
            return

        source = self.languages[self.source_lang.get()]
        target = self.languages[self.target_lang.get()]

        if source == target:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", text)
            self.output_text.config(state=tk.DISABLED)
            self.show_status("Source and target languages are the same", "info")
            return

        self.translate_btn.config(state=tk.DISABLED, text="Translating...")
        self.show_status("Translating...", "loading")

        thread = threading.Thread(target=self._perform_translation, args=(text, source, target))
        thread.daemon = True
        thread.start()

    def _perform_translation(self, text, source, target):
        try:
            if source == "auto":
                translator = GoogleTranslator(source="auto", target=target)
            else:
                translator = GoogleTranslator(source=source, target=target)

            translated_text = translator.translate(text)
            self.root.after(0, self._update_translation, translated_text, None)
        except Exception as e:
            self.root.after(0, self._update_translation, None, str(e))

    def _update_translation(self, translated_text, error):
        self.translate_btn.config(state=tk.NORMAL, text="Translate")

        if error:
            self.show_status(f"Error: {error}. Please try again.", "error")
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", "Translation failed. Please try again.")
            self.output_text.config(state=tk.DISABLED)
        else:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", translated_text)
            self.output_text.config(state=tk.DISABLED)
            self.show_status("Translation completed successfully!", "success")

    def copy_translation(self):
        text = self.output_text.get("1.0", tk.END).strip()

        if not text or text == "Translation will appear here..." or text == "Translation failed. Please try again.":
            self.show_status("No translation to copy", "error")
            return

        try:
            pyperclip.copy(text)
            self.show_status("Copied to clipboard!", "success")
        except Exception:
            try:
                root = tk.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                root.after(100)
                root.destroy()
                self.show_status("Copied to clipboard!", "success")
            except Exception as e:
                self.show_status(f"Failed to copy: {e}", "error")

    def speak_translation(self):
        text = self.output_text.get("1.0", tk.END).strip()

        if not text or text == "Translation will appear here..." or text == "Translation failed. Please try again.":
            self.show_status("No translation to speak", "error")
            return

        self.speak_btn.config(state=tk.DISABLED, text="Speaking...")
        thread = threading.Thread(target=self._speak_text, args=(text,))
        thread.daemon = True
        thread.start()

    def _speak_text(self, text):
        try:
            lang_name = self.target_lang.get()
            lang_code = self.languages.get(lang_name, "en")
            if lang_code == "auto":
                lang_code = "en"

            tts = gTTS(text=text, lang=lang_code)
            temp_file = os.path.join(tempfile.gettempdir(), "translation_speech.mp3")
            tts.save(temp_file)

            try:
                from playsound import playsound
                playsound(temp_file)
            except Exception:
                os.system(f'start "" "{temp_file}"')

            try:
                os.remove(temp_file)
            except Exception:
                pass

            self.root.after(0, lambda: self.speak_btn.config(state=tk.NORMAL, text="🔊 Speak"))
        except Exception as e:
            self.root.after(0, lambda: self.speak_btn.config(state=tk.NORMAL, text="🔊 Speak"))
            self.root.after(0, lambda: self.show_status(f"Text-to-speech failed: {e}", "error"))


def main():
    root = tk.Tk()
    app = TranslationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()