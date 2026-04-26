import tkinter as tk
from tkinter import ttk
from utils.theme import *


def styled_button(parent, text, command=None, style="primary", **kw):
    colors = {
        "primary": (ACCENT, BG_DARK),
        "secondary": (BG_PANEL, TEXT_PRIMARY),
        "danger": (DANGER, "#fff"),
        "success": (SUCCESS, "#fff"),
        "ghost": (BG_DARK, ACCENT),
    }
    bg, fg = colors.get(style, (ACCENT, BG_DARK))
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        font=FONT_BTN,
        relief="flat", cursor="hand2",
        padx=18, pady=8,
        activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
        bd=0, **kw
    )
    return btn


def card_frame(parent, title=None, **kw):
    outer = tk.Frame(parent, bg=BORDER, bd=0)
    inner = tk.Frame(outer, bg=BG_CARD, bd=0, padx=16, pady=12)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    if title:
        tk.Label(inner, text=title, bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(anchor="w")
    return outer, inner


def labeled_entry(parent, label, show=None, **kw):
    frame = tk.Frame(parent, bg=BG_CARD)
    tk.Label(frame, text=label, bg=BG_CARD, fg=TEXT_SECONDARY,
             font=FONT_SMALL).pack(anchor="w", pady=(4, 2))
    var = tk.StringVar()
    entry = tk.Entry(frame, textvariable=var, bg=BG_INPUT, fg=TEXT_PRIMARY,
                     font=FONT_BODY, relief="flat", bd=0,
                     insertbackground=ACCENT, show=show or "",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT, **kw)
    entry.pack(fill="x", ipady=6)
    return frame, var


def labeled_combo(parent, label, values, **kw):
    frame = tk.Frame(parent, bg=BG_CARD)
    tk.Label(frame, text=label, bg=BG_CARD, fg=TEXT_SECONDARY,
             font=FONT_SMALL).pack(anchor="w", pady=(4, 2))
    var = tk.StringVar()
    style = ttk.Style()
    style.configure("Dark.TCombobox",
                    fieldbackground=BG_INPUT,
                    background=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=ACCENT,
                    borderwidth=0)
    combo = ttk.Combobox(frame, textvariable=var, values=values,
                         style="Dark.TCombobox", font=FONT_BODY,
                         state="readonly", **kw)
    combo.pack(fill="x", ipady=4)
    if values:
        combo.current(0)
    return frame, var


def kpi_card(parent, title, value, color=ACCENT, icon=""):
    frame = tk.Frame(parent, bg=BG_CARD, padx=16, pady=14)
    # Top accent line
    accent_bar = tk.Frame(frame, bg=color, height=3)
    accent_bar.pack(fill="x", pady=(0, 10))
    tk.Label(frame, text=f"{icon}  {title}" if icon else title,
             bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_KPI_LABEL).pack(anchor="w")
    tk.Label(frame, text=str(value), bg=BG_CARD, fg=color,
             font=FONT_KPI_VAL).pack(anchor="w", pady=(4, 0))
    return frame


def section_title(parent, text, bg=BG_DARK):
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=text, bg=bg, fg=TEXT_PRIMARY,
             font=FONT_SUBHEAD).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=12, pady=8)
    return f


def scrollable_frame(parent, bg=BG_DARK):
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas, bg=bg)
    scrollable.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return container, scrollable


def toast(root, message, color=SUCCESS):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(bg=color)
    tk.Label(popup, text=f"  {message}  ", bg=color, fg="#fff",
             font=FONT_BODY, padx=10, pady=8).pack()
    # Position bottom-right
    root.update_idletasks()
    w, h = 300, 40
    x = root.winfo_x() + root.winfo_width() - w - 20
    y = root.winfo_y() + root.winfo_height() - h - 40
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.after(2500, popup.destroy)
