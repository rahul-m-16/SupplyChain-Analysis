import tkinter as tk
from utils.theme import *


class AboutPage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref = app_ref
        self._build()

    def _build(self):
        container = tk.Frame(self, bg=BG_DARK, padx=60, pady=40)
        container.pack(fill="both", expand=True)

        # Hero
        tk.Label(container, text="About This Platform",
                 bg=BG_DARK, fg=ACCENT, font=FONT_TITLE).pack(anchor="w")
        tk.Label(container, text="A comprehensive supply chain data analytics suite built with Python & SQL Server",
                 bg=BG_DARK, fg=TEXT_SECONDARY, font=("Segoe UI", 13)).pack(anchor="w", pady=(4, 24))
        tk.Frame(container, bg=BORDER, height=1).pack(fill="x", pady=(0, 24))

        # Project overview
        section = tk.Frame(container, bg=BG_DARK)
        section.pack(fill="x", pady=8)
        tk.Label(section, text="PROJECT OVERVIEW", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))
        overview_text = (
            "This platform provides end-to-end supply chain visibility by connecting "
            "directly to a SQL Server database and rendering rich analytics dashboards. "
            "It enables users to register, log in, enter new supply chain records, and "
            "explore multi-dimensional charts and KPIs across orders, delivery performance, "
            "customer segments, markets, and product categories."
        )
        tk.Label(section, text=overview_text, bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=FONT_BODY, wraplength=700, justify="left").pack(anchor="w")

        tk.Frame(container, bg=BORDER, height=1).pack(fill="x", pady=16)

        # Data columns
        tk.Label(container, text="DATA COLUMNS", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 10))

        cols_frame = tk.Frame(container, bg=BG_DARK)
        cols_frame.pack(fill="x")

        columns = [
            ("Type", "Payment type (DEBIT/TRANSFER etc.)"),
            ("Days_for_shipping_(real)", "Actual shipping duration in days"),
            ("Days_for_shipment_(scheduled)", "Planned shipping duration"),
            ("Benefit_per_order", "Profit benefit per individual order"),
            ("Sales_per_customer", "Total sales value per customer"),
            ("Delivery_Status", "Current delivery status"),
            ("Late_delivery_risk", "Binary risk flag (0/1)"),
            ("Category_Name", "Product category name"),
            ("Customer_Segment", "Consumer / Corporate / Home Office"),
            ("Market", "Geographic market region"),
            ("Order_Status", "COMPLETE / PENDING / CANCELLED etc."),
            ("Shipping_Mode", "First Class / Second Class / Standard etc."),
            ("Sales", "Order line item sales value"),
            ("Order_Profit_Per_Order", "Profit earned on order"),
            ("Product_Name", "Full product name"),
            ("Department_Name", "Department responsible for product"),
        ]

        for i, (col, desc) in enumerate(columns):
            row_bg = BG_CARD if i % 2 == 0 else BG_PANEL
            row = tk.Frame(cols_frame, bg=row_bg, padx=12, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=col, bg=row_bg, fg=ACCENT, font=FONT_MONO,
                     width=36, anchor="w").pack(side="left")
            tk.Label(row, text=desc, bg=row_bg, fg=TEXT_SECONDARY,
                     font=FONT_SMALL, anchor="w").pack(side="left")

        tk.Frame(container, bg=BORDER, height=1).pack(fill="x", pady=16)

        # Tech stack
        tk.Label(container, text="TECHNOLOGY STACK", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 10))

        tech_frame = tk.Frame(container, bg=BG_DARK)
        tech_frame.pack(fill="x")

        techs = [
            ("Python 3.x", "Core application language", ACCENT),
            ("Tkinter", "GUI framework for desktop UI", ACCENT2),
            ("pyodbc", "SQL Server connectivity", ACCENT3),
            ("matplotlib", "Charts and data visualization", ACCENT4),
            ("SQL Server Express", "Relational database backend", ACCENT5),
        ]
        for i, (tech, desc, color) in enumerate(techs):
            f = tk.Frame(tech_frame, bg=BG_CARD, padx=14, pady=10)
            f.grid(row=0, column=i, padx=6, sticky="nsew")
            tk.Frame(f, bg=color, height=3).pack(fill="x", pady=(0, 8))
            tk.Label(f, text=tech, bg=BG_CARD, fg=color,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(f, text=desc, bg=BG_CARD, fg=TEXT_SECONDARY,
                     font=FONT_SMALL, wraplength=130).pack(anchor="w", pady=(2, 0))
            tech_frame.columnconfigure(i, weight=1)
