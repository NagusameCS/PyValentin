from tkinter import ttk
import sys
import platform

# Detect if running as bundled application
IS_BUNDLED = getattr(sys, 'frozen', False)

def setup_styles():
    """Configure application styles with platform-specific adjustments"""
    style = ttk.Style()
    
    # Base styles
    base_styles = {
        'TButton': {
            'font': ('Helvetica', 12),
            'background': '#007acc',
            'foreground': '#ffffff',
            'focuscolor': '#007acc',
            'borderwidth': 0,
            'highlightthickness': 0
        },
        'TLabel': {
            'font': ('Helvetica', 12),
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
            'borderwidth': 0,
            'highlightthickness': 0
        },
        'TEntry': {
            'font': ('Helvetica', 12),
            'fieldbackground': '#252526',
            'foreground': '#d4d4d4',
            'borderwidth': 1,
            'highlightthickness': 0,
            'selectbackground': '#264f78',
            'selectforeground': '#ffffff'
        }
    }
    
    # Platform-specific adjustments
    if platform.system() == 'Darwin':  # macOS
        base_styles['TButton']['padding'] = 10
        base_styles['TEntry']['padding'] = 5
    else:  # Windows and others
        base_styles['TButton']['padding'] = 8
        base_styles['TEntry']['padding'] = 4
    
    # Apply styles
    for widget, config in base_styles.items():
        style.configure(widget, **config)
