import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Window settings
        self.title("PyValentin")
        self.geometry("400x400")
        self.overrideredirect(True)  # Remove window decorations
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"400x400+{x}+{y}")

        # Keep window on top
        self.wm_attributes('-topmost', True)
        
        # Create frame with dark background
        self.frame = tk.Frame(self, bg='#1e1e1e', width=400, height=400)
        self.frame.pack(fill='both', expand=True)

        # Add title
        title = tk.Label(self.frame, 
                        text="PyValentin",
                        font=('Helvetica', 24, 'bold'),
                        bg='#1e1e1e',
                        fg='#d4d4d4')
        title.pack(pady=(100,10))

        # Add loading text
        self.loading_label = tk.Label(self.frame,
                                    text="Loading...",
                                    font=('Helvetica', 12),
                                    bg='#1e1e1e',
                                    fg='#007acc')
        self.loading_label.pack(pady=10)

        # Add progress bar
        self.progress = tk.Canvas(self.frame,
                                width=200,
                                height=2,
                                bg='#252526',
                                highlightthickness=0)
        self.progress.pack(pady=20)
        
        self.progress_bar = self.progress.create_rectangle(0, 0, 0, 2, fill='#007acc')
        self.progress_value = 0

    def update_progress(self, value):
        """Update progress bar value (0-100)"""
        self.progress_value = value
        width = (value / 100) * 200
        self.progress.coords(self.progress_bar, 0, 0, width, 2)
        self.update()

    def finish(self):
        """Close splash screen"""
        self.destroy()
