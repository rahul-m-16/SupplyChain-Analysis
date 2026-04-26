import tkinter as tk
from utils.theme import *
from utils.db import login_user, register_user
from components.widgets import toast

PLACEHOLDER_COLOR = "#555e68"


def _ph_entry(parent, placeholder, show=None, width=30):
    entry = tk.Entry(parent, bg=BG_INPUT, fg=PLACEHOLDER_COLOR,
                     font=FONT_BODY, relief="flat", bd=0,
                     insertbackground=ACCENT, show="" , width=width,
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT)
    entry.insert(0, placeholder)
    entry._placeholder = placeholder
    entry._show        = show or ""

    def _in(e):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=TEXT_PRIMARY, show=entry._show)
    def _out(e):
        if not entry.get().strip():
            entry.config(show="")
            entry.insert(0, placeholder)
            entry.config(fg=PLACEHOLDER_COLOR)

    entry.bind("<FocusIn>",  _in)
    entry.bind("<FocusOut>", _out)
    return entry


class AuthPage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref = app_ref
        self.mode    = "signin"
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        # Center card
        card = tk.Frame(self, bg=BG_CARD, padx=44, pady=38)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo & title
        tk.Label(card, text="⛓", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI", 30)).pack()
        title = "Welcome Back" if self.mode == "signin" else "Create Account"
        sub   = "Sign in to your account" if self.mode == "signin" else "Register a new account"
        tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 20, "bold")).pack(pady=(6, 2))
        tk.Label(card, text=sub, bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack()
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=18)

        # ── Fields ───────────────────────────────────────────
        def field(label, placeholder, show=None):
            tk.Label(card, text=label, bg=BG_CARD, fg=TEXT_SECONDARY,
                     font=FONT_SMALL).pack(anchor="w", pady=(6,2))
            e = _ph_entry(card, placeholder, show=show, width=32)
            e.pack(fill="x", ipady=6)
            return e

        if self.mode == "register":
            self.e_email = field("Email Address", "you@example.com")

        self.e_user = field("Username", "Enter username")
        self.e_pass = field("Password", "Enter password", show="●")

        if self.mode == "register":
            self.e_cpass = field("Confirm Password", "Re-enter password", show="●")

        # Error label
        self.err = tk.Label(card, text="", bg=BG_CARD, fg=DANGER, font=FONT_SMALL,
                            wraplength=300)
        self.err.pack(pady=(10, 0))

        # Submit button
        btn_text = "Sign In" if self.mode == "signin" else "Register"
        cmd      = self._signin if self.mode == "signin" else self._register
        tk.Button(card, text=btn_text, command=cmd,
                  bg=ACCENT, fg=BG_DARK, font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2", padx=20, pady=9,
                  activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY
                  ).pack(fill="x", pady=(16, 6))

        # Toggle link
        tog_text = "Don't have an account?  Register →" if self.mode == "signin" \
                   else "Already have an account?  Sign In →"
        tk.Button(card, text=tog_text, bg=BG_CARD, fg=INFO,
                  font=FONT_SMALL, relief="flat", cursor="hand2", bd=0,
                  command=self._toggle).pack()

    def _val(self, e):
        v = e.get().strip()
        return "" if v == e._placeholder else v

    def _toggle(self):
        self.mode = "register" if self.mode == "signin" else "signin"
        self._build()

    def _signin(self):
        u, p = self._val(self.e_user), self._val(self.e_pass)
        if not u or not p:
            self.err.config(text="Please fill in all fields."); return
        ok, res = login_user(u, p)
        if ok:
            self.app_ref.set_user(res)
            toast(self.app_ref, f"Welcome back, {res['username']}!", SUCCESS)
            self.app_ref.navigate("home")
        else:
            self.err.config(text=res)

    def _register(self):
        email  = self._val(self.e_email)
        u      = self._val(self.e_user)
        p      = self._val(self.e_pass)
        cp     = self._val(self.e_cpass)
        if not all([email, u, p, cp]):
            self.err.config(text="Please fill in all fields."); return
        if p != cp:
            self.err.config(text="Passwords do not match."); return
        if len(p) < 6:
            self.err.config(text="Password must be at least 6 characters."); return
        ok, msg = register_user(u, email, p)
        if ok:
            toast(self.app_ref, "Account created! Please sign in.", SUCCESS)
            self.mode = "signin"
            self._build()
        else:
            self.err.config(text=msg)
