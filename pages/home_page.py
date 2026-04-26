import tkinter as tk
from utils.theme import *
from utils.db import get_total_records, fetch_kpis
from components.widgets import kpi_card


class HomePage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref = app_ref
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=BG_DARK, pady=32, padx=40)
        header.pack(fill="x")
        tk.Label(header, text="Supply Chain", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 36, "bold")).pack(anchor="w")
        tk.Label(header, text="Analytics & Intelligence Platform",
                 bg=BG_DARK, fg=TEXT_SECONDARY, font=("Segoe UI", 14)).pack(anchor="w")

        # Decorative bar
        bar = tk.Frame(self, bg=BG_DARK, padx=40)
        bar.pack(fill="x")
        colors = [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5]
        for c in colors:
            tk.Frame(bar, bg=c, height=3, width=60).pack(side="left", padx=2)

        # Stats row
        stats_frame = tk.Frame(self, bg=BG_DARK, padx=40, pady=30)
        stats_frame.pack(fill="x")
        tk.Label(stats_frame, text="LIVE STATISTICS",
                 bg=BG_DARK, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 12))

        cards_row = tk.Frame(stats_frame, bg=BG_DARK)
        cards_row.pack(fill="x")

        try:
            kpis = fetch_kpis()
            total = get_total_records()
            stats = [
                ("Total Records", f"{total:,}", ACCENT, "📦"),
                ("Total Sales", f"${kpis['total_sales']:,.0f}", ACCENT3, "💰"),
                ("Total Profit", f"${kpis['total_profit']:,.0f}", ACCENT4, "📈"),
                ("Late Delivery %", f"{kpis['late_delivery_pct']}%", DANGER, "⚠️"),
                ("Avg Ship Days", f"{kpis['avg_shipping_days']:.1f}d", ACCENT2, "🚚"),
            ]
        except Exception as e:
            stats = [("DB Error", str(e)[:30], DANGER, "❌")]

        for i, (title, val, color, icon) in enumerate(stats):
            card = kpi_card(cards_row, title, val, color, icon)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            cards_row.columnconfigure(i, weight=1)

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=40, pady=8)

        # Feature highlights
        features_frame = tk.Frame(self, bg=BG_DARK, padx=40, pady=20)
        features_frame.pack(fill="both", expand=True)
        tk.Label(features_frame, text="PLATFORM FEATURES",
                 bg=BG_DARK, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 16))

        feat_grid = tk.Frame(features_frame, bg=BG_DARK)
        feat_grid.pack(fill="x")

        features = [
            ("📊", "7+ Visual Analytics", "Interactive charts with deep supply chain insights", ACCENT),
            ("🔍", "Smart Filtering", "Multi-column filter system for precise analysis", ACCENT2),
            ("➕", "Data Entry", "Add new records directly to SQL Server database", ACCENT3),
            ("🔐", "Secure Access", "User registration, authentication and session mgmt", ACCENT4),
            ("🌍", "Global Markets", "Analyze performance across all world markets", ACCENT5),
            ("⚡", "Real-time KPIs", "Live KPI cards pulled from SQL Server", INFO),
        ]
        for i, (icon, title, desc, color) in enumerate(features):
            col = i % 3
            row = i // 3
            card = tk.Frame(feat_grid, bg=BG_CARD, padx=16, pady=14)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            tk.Label(card, text=icon, bg=BG_CARD, fg=color, font=("Segoe UI", 20)).pack(anchor="w")
            tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_PRIMARY,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 2))
            tk.Label(card, text=desc, bg=BG_CARD, fg=TEXT_SECONDARY,
                     font=FONT_SMALL, wraplength=220, justify="left").pack(anchor="w")
            feat_grid.columnconfigure(col, weight=1)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
