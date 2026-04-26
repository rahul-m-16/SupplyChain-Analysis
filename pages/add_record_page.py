import tkinter as tk
from tkinter import ttk
from utils.theme import *
from utils.db import insert_record, get_total_records
from components.widgets import styled_button, toast, scrollable_frame

FIELDS = [
    ("Type",                        "Payment Type",              "combo",  ["DEBIT","TRANSFER","PAYMENT","CASH"]),
    ("Days_for_shipping_real",      "Days for Shipping (Real)",  "entry",  "e.g. 3"),
    ("Days_for_shipment_scheduled", "Days for Shipment (Sched)", "entry",  "e.g. 2"),
    ("Benefit_per_order",           "Benefit Per Order ($)",     "entry",  "e.g. 48.10"),
    ("Sales_per_customer",          "Sales Per Customer ($)",    "entry",  "e.g. 129.99"),
    ("Delivery_Status",             "Delivery Status",           "combo",  ["Advance shipping","Late delivery","Shipping canceled","Shipping on time"]),
    ("Late_delivery_risk",          "Late Delivery Risk",        "combo",  ["0","1"]),
    ("Category_Id",                 "Category ID",               "entry",  "e.g. 18"),
    ("Category_Name",               "Category Name",             "entry",  "e.g. Men's Footwear"),
    ("Customer_City",               "Customer City",             "entry",  "e.g. Caguas"),
    ("Customer_Country",            "Customer Country",          "entry",  "e.g. Puerto Rico"),
    ("Customer_Fname",              "Customer First Name",       "entry",  "e.g. Mary"),
    ("Customer_Id",                 "Customer ID",               "entry",  "e.g. 9619"),
    ("Customer_Lname",              "Customer Last Name",        "entry",  "e.g. Smith"),
    ("Customer_Segment",            "Customer Segment",          "combo",  ["Consumer","Corporate","Home Office"]),
    ("Customer_State",              "Customer State",            "entry",  "e.g. PR"),
    ("Customer_Zipcode",            "Customer Zipcode",          "entry",  "e.g. 725"),
    ("Department_Id",               "Department ID",             "entry",  "e.g. 4"),
    ("Department_Name",             "Department Name",           "entry",  "e.g. Apparel"),
    ("Market",                      "Market",                    "combo",  ["Africa","Europe","LATAM","Pacific Asia","USCA"]),
    ("Order_City",                  "Order City",                "entry",  "e.g. Vicenza"),
    ("Order_Country",               "Order Country",             "entry",  "e.g. Italia"),
    ("Order_Customer_Id",           "Order Customer ID",         "entry",  "e.g. 9619"),
    ("order_date_DateOrders",       "Order Date",                "entry",  "e.g. 7/13/2015 3:24"),
    ("Order_Id",                    "Order ID *",                "entry",  "e.g. 13232"),
    ("Order_Item_Cardprod_Id",      "Card Product ID",           "entry",  "e.g. 403"),
    ("Order_Item_Discount",         "Item Discount ($)",         "entry",  "e.g. 0.00"),
    ("Order_Item_Discount_Rate",    "Item Discount Rate",        "entry",  "e.g. 0.03"),
    ("Order_Item_Id",               "Order Item ID",             "entry",  "e.g. 33103"),
    ("Order_Item_Product_Price",    "Item Product Price ($)",    "entry",  "e.g. 129.99"),
    ("Order_Item_Profit_Ratio",     "Item Profit Ratio",         "entry",  "e.g. 0.37"),
    ("Order_Item_Quantity",         "Item Quantity",             "entry",  "e.g. 1"),
    ("Sales",                       "Sales ($)",                 "entry",  "e.g. 129.99"),
    ("Order_Item_Total",            "Order Item Total ($)",      "entry",  "e.g. 129.99"),
    ("Order_Profit_Per_Order",      "Profit Per Order ($)",      "entry",  "e.g. 48.10"),
    ("Order_Region",                "Order Region",              "entry",  "e.g. Southern Europe"),
    ("Order_State",                 "Order State",               "entry",  "e.g. Veneto"),
    ("Order_Status",                "Order Status",              "combo",  ["COMPLETE","PENDING","PENDING_PAYMENT","PROCESSING","PAYMENT_REVIEW","CLOSED","SUSPECTED_FRAUD","ON_HOLD","CANCELED"]),
    ("Product_Card_Id",             "Product Card ID",           "entry",  "e.g. 403"),
    ("Product_Category_Id",         "Product Category ID",       "entry",  "e.g. 18"),
    ("Product_Name",                "Product Name *",            "entry",  "e.g. Nike Men's CJ Elite 2 TD Football Cleat"),
    ("Product_Price",               "Product Price ($)",         "entry",  "e.g. 129.99"),
    ("shipping_date_DateOrders",    "Shipping Date",             "entry",  "e.g. 7/16/2015 3:24"),
    ("Shipping_Mode",               "Shipping Mode",             "combo",  ["First Class","Second Class","Standard Class","Same Day"]),
]

PH_COLOR = "#555e68"


def _styled_combo(parent, options):
    """Custom-drawn combo that looks identical to Entry fields."""
    var  = tk.StringVar(value=options[0])
    frame = tk.Frame(parent, bg=BG_INPUT, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)

    selected_lbl = tk.Label(frame, textvariable=var, bg=BG_INPUT, fg=TEXT_PRIMARY,
                            font=FONT_BODY, anchor="w", padx=8, pady=5, cursor="hand2")
    selected_lbl.pack(side="left", fill="both", expand=True)

    arrow = tk.Label(frame, text="▾", bg=BG_INPUT, fg=ACCENT,
                     font=("Segoe UI", 9), padx=6, cursor="hand2")
    arrow.pack(side="right")

    popup = None

    def show_popup(e=None):
        nonlocal popup
        if popup and popup.winfo_exists():
            popup.destroy(); return

        popup = tk.Toplevel(frame)
        popup.overrideredirect(True)
        popup.configure(bg=BORDER)
        popup.attributes("-topmost", True)

        frame.update_idletasks()
        x = frame.winfo_rootx()
        y = frame.winfo_rooty() + frame.winfo_height()
        w = frame.winfo_width()
        popup.geometry(f"{w}x{min(len(options)*28+2, 200)}+{x}+{y}")

        # scrollable list
        canvas = tk.Canvas(popup, bg=BG_INPUT, highlightthickness=0)
        sb     = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        inner  = tk.Frame(canvas, bg=BG_INPUT)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        for opt in options:
            def make_cmd(o=opt):
                def cmd():
                    var.set(o)
                    selected_lbl.config(fg=TEXT_PRIMARY)
                    popup.destroy()
                return cmd
            row = tk.Frame(inner, bg=BG_INPUT, cursor="hand2")
            row.pack(fill="x")
            lbl = tk.Label(row, text=opt, bg=BG_INPUT, fg=TEXT_PRIMARY,
                           font=FONT_BODY, anchor="w", padx=10, pady=5)
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", lambda e, c=make_cmd(): c())
            row.bind("<Button-1>", lambda e, c=make_cmd(): c())
            lbl.bind("<Enter>", lambda e, r=row, l=lbl: (r.config(bg=BG_HOVER), l.config(bg=BG_HOVER)))
            lbl.bind("<Leave>", lambda e, r=row, l=lbl: (r.config(bg=BG_INPUT), l.config(bg=BG_INPUT)))

        popup.bind("<FocusOut>", lambda e: popup.destroy() if popup.winfo_exists() else None)
        popup.focus_set()

    selected_lbl.bind("<Button-1>", show_popup)
    arrow.bind("<Button-1>", show_popup)
    frame.bind("<Button-1>", show_popup)

    frame._var = var
    frame.focus_in  = lambda: frame.config(highlightbackground=ACCENT)
    frame.focus_out = lambda: frame.config(highlightbackground=BORDER)
    return frame, var


def _ph_entry(parent, placeholder, width=34):
    entry = tk.Entry(parent, bg=BG_INPUT, fg=PH_COLOR, font=FONT_BODY,
                     relief="flat", bd=0, insertbackground=ACCENT, width=width,
                     highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
    entry.insert(0, placeholder)
    entry._placeholder = placeholder

    def _in(e):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=TEXT_PRIMARY)
    def _out(e):
        if not entry.get().strip():
            entry.insert(0, placeholder)
            entry.config(fg=PH_COLOR)

    entry.bind("<FocusIn>",  _in)
    entry.bind("<FocusOut>", _out)
    return entry


class AddRecordPage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref = app_ref
        self.entries = {}
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, padx=36, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="➕  Add New Record", bg=BG_DARK, fg=ACCENT,
                 font=FONT_HEADING).pack(side="left")
        self.count_lbl = tk.Label(hdr, text="", bg=BG_DARK, fg=TEXT_SECONDARY, font=FONT_SMALL)
        self.count_lbl.pack(side="right")
        self._refresh_count()
        tk.Label(hdr, text="* required fields", bg=BG_DARK, fg=TEXT_MUTED, font=FONT_SMALL).pack(side="right", padx=12)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=36)

        sc, sf = scrollable_frame(self)
        sc.pack(fill="both", expand=True, padx=36, pady=12)

        grid = tk.Frame(sf, bg=BG_DARK)
        grid.pack(fill="x")

        for i, (key, label, ftype, extra) in enumerate(FIELDS):
            col_n = i % 2
            row_n = i // 2
            cell  = tk.Frame(grid, bg=BG_DARK, padx=8, pady=5)
            cell.grid(row=row_n, column=col_n, sticky="ew")
            grid.columnconfigure(col_n, weight=1)

            tk.Label(cell, text=label, bg=BG_DARK, fg=TEXT_SECONDARY,
                     font=FONT_SMALL).pack(anchor="w", pady=(0, 3))

            if ftype == "combo":
                widget, var = _styled_combo(cell, extra)
                widget.pack(fill="x", ipady=0)
                self.entries[key] = (widget, var, "combo")
            else:
                entry = _ph_entry(cell, extra)
                entry.pack(fill="x", ipady=5)
                self.entries[key] = (entry, None, "entry")

        btn_bar = tk.Frame(sf, bg=BG_DARK, pady=18)
        btn_bar.pack(fill="x", padx=8)
        styled_button(btn_bar, "✅  Submit Record", command=self._submit, style="primary").pack(side="left", padx=4)
        styled_button(btn_bar, "🔄  Clear Form",    command=self._clear,  style="secondary").pack(side="left", padx=4)

        self.status = tk.Label(sf, text="", bg=BG_DARK, fg=TEXT_SECONDARY, font=FONT_SMALL)
        self.status.pack(pady=(0, 20))

    def _refresh_count(self):
        try:
            n = get_total_records()
            self.count_lbl.config(text=f"📦 Total records: {n:,}", fg=ACCENT3)
        except Exception as e:
            self.count_lbl.config(text=f"DB Error: {e}", fg=DANGER)

    def _get_val(self, key):
        widget, var, ftype = self.entries[key]
        if ftype == "combo":
            return var.get().strip()
        else:
            v = widget.get().strip()
            return "" if v == widget._placeholder else v

    def _submit(self):
        if not self.app_ref.current_user:
            toast(self.app_ref, "Please sign in to add records.", DANGER)
            self.app_ref.navigate("signin"); return

        for req in ("Order_Id", "Product_Name"):
            if not self._get_val(req):
                self.status.config(text=f"⚠  '{req}' is required.", fg=WARNING); return

        data = {k: self._get_val(k) for k, _, _, _ in FIELDS if self._get_val(k)}
        try:
            insert_record(data)
            self._refresh_count()
            toast(self.app_ref, "Record inserted! View in Records page.", SUCCESS)
            self.status.config(text="✅ Saved to SQL Server.", fg=SUCCESS)
        except Exception as e:
            self.status.config(text=f"❌ {e}", fg=DANGER)

    def _clear(self):
        for key, _, ftype, extra in FIELDS:
            widget, var, _ = self.entries[key]
            if ftype == "combo":
                var.set(extra[0])
            else:
                widget.delete(0, "end")
                widget.insert(0, widget._placeholder)
                widget.config(fg=PH_COLOR)
        self.status.config(text="")
