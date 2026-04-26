import tkinter as tk
from utils.theme import *


NAV_ITEMS = [
    ("🏠", "Home",       "home"),
    ("📊", "Analysis",   "analysis"),
    ("➕", "Add Record", "add_record"),
    ("📋", "Records",    "records"),
    ("ℹ️", "About",      "about"),
]


class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate, app_ref, **kw):
        super().__init__(parent, bg=BG_CARD, width=SIDEBAR_W, **kw)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.app_ref = app_ref
        self.buttons = {}
        self.current = "home"
        self._build()

    def _build(self):
        # Logo
        logo_frame = tk.Frame(self, bg=BG_CARD, pady=24)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="⛓", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI", 26)).pack()
        tk.Label(logo_frame, text="SupplyChain", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 13, "bold")).pack()
        tk.Label(logo_frame, text="Analytics Suite", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack()
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)

        # Nav items
        nav_frame = tk.Frame(self, bg=BG_CARD)
        nav_frame.pack(fill="x", padx=8)
        for icon, label, page in NAV_ITEMS:
            btn = self._make_nav_btn(nav_frame, icon, label, page)
            self.buttons[page] = btn

        # Spacer
        tk.Frame(self, bg=BG_CARD).pack(fill="both", expand=True)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)

        # User info + logout
        self.user_frame = tk.Frame(self, bg=BG_CARD, pady=12)
        self.user_frame.pack(fill="x", padx=12)
        self.user_label = tk.Label(self.user_frame, text="Not logged in",
                                   bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_SMALL,
                                   wraplength=160)
        self.user_label.pack(anchor="w")
        self.auth_btn = tk.Button(self.user_frame, text="Sign In",
                                  bg=ACCENT, fg=BG_DARK, font=FONT_BTN,
                                  relief="flat", cursor="hand2", padx=12, pady=5,
                                  command=lambda: self.on_navigate("signin"))
        self.auth_btn.pack(anchor="w", pady=(6, 0))

    def _make_nav_btn(self, parent, icon, label, page):
        frame = tk.Frame(parent, bg=BG_CARD, cursor="hand2")
        frame.pack(fill="x", pady=2)
        lbl = tk.Label(frame, text=f"  {icon}  {label}", bg=BG_CARD,
                       fg=TEXT_SECONDARY, font=FONT_NAV, anchor="w",
                       padx=8, pady=10)
        lbl.pack(fill="x")
        indicator = tk.Frame(frame, bg=BG_CARD, width=4)
        indicator.place(relx=0, rely=0, relheight=1)

        def on_click(p=page, f=frame, l=lbl, ind=indicator):
            self.set_active(p)
            self.on_navigate(p)

        def on_enter(e, f=frame, l=lbl):
            if self.current != page:
                f.config(bg=BG_HOVER)
                l.config(bg=BG_HOVER)

        def on_leave(e, f=frame, l=lbl):
            if self.current != page:
                f.config(bg=BG_CARD)
                l.config(bg=BG_CARD)

        frame.bind("<Button-1>", lambda e: on_click())
        lbl.bind("<Button-1>", lambda e: on_click())
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)
        frame._indicator = indicator
        frame._label = lbl
        return frame

    def set_active(self, page):
        for p, frame in self.buttons.items():
            if p == page:
                frame.config(bg=BG_PANEL)
                frame._label.config(bg=BG_PANEL, fg=ACCENT)
                frame._indicator.config(bg=ACCENT)
            else:
                frame.config(bg=BG_CARD)
                frame._label.config(bg=BG_CARD, fg=TEXT_SECONDARY)
                frame._indicator.config(bg=BG_CARD)
        self.current = page

    def update_user(self, username=None):
        if username:
            self.user_label.config(text=f"👤 {username}", fg=ACCENT3)
            self.auth_btn.config(text="Sign Out", bg=DANGER, fg="#fff",
                                 command=self.app_ref.logout)
        else:
            self.user_label.config(text="Not logged in", fg=TEXT_SECONDARY)
            self.auth_btn.config(text="Sign In", bg=ACCENT, fg=BG_DARK,
                                 command=lambda: self.on_navigate("signin"))
