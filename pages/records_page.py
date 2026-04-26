import tkinter as tk
from tkinter import ttk
from utils.theme import *
from utils.db import get_connection, get_total_records, fetch_distinct, col
from components.widgets import toast

PAGE_SIZE = 100   # rows per page

# Columns to display in the table (logical names)
DISPLAY_COLS = [
    "orderid", "orderdatedateorders", "type",
    "customerfname", "customerlname", "customersegment",
    "market", "orderstatus", "deliverystatus",
    "shippingmode", "daysforshippingreal",
    "latedeliveryrisk", "categoryname",
    "productname", "sales", "orderprofitperorder",
]

DISPLAY_HEADERS = [
    "Order ID", "Order Date", "Type",
    "First Name", "Last Name", "Segment",
    "Market", "Order Status", "Delivery",
    "Ship Mode", "Ship Days",
    "Late Risk", "Category",
    "Product", "Sales ($)", "Profit ($)",
]

COL_WIDTHS = [80,130,80,90,90,90,90,110,120,110,70,70,130,220,90,90]


class RecordsPage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref  = app_ref
        self._offset  = 0
        self._total   = 0
        self._filter_vars = {}
        self._search_var  = tk.StringVar()
        self._build()

    # ── Layout ────────────────────────────────────────────
    def _build(self):
        # Header bar
        hdr = tk.Frame(self, bg=BG_DARK, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📋  Records Viewer", bg=BG_DARK, fg=ACCENT,
                 font=FONT_HEADING).pack(side="left")
        self.count_lbl = tk.Label(hdr, text="", bg=BG_DARK, fg=TEXT_SECONDARY, font=FONT_SMALL)
        self.count_lbl.pack(side="right")

        # Search + filter bar
        fb = tk.Frame(self, bg=BG_PANEL, padx=20, pady=8)
        fb.pack(fill="x")

        # Search box
        tk.Label(fb, text="🔍", bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT_BODY).pack(side="left")
        self.search_entry = tk.Entry(fb, textvariable=self._search_var,
                                     bg=BG_INPUT, fg=TEXT_PRIMARY, font=FONT_BODY,
                                     relief="flat", bd=0, insertbackground=ACCENT, width=22,
                                     highlightthickness=1, highlightbackground=BORDER,
                                     highlightcolor=ACCENT)
        self.search_entry.pack(side="left", ipady=5, padx=(4, 14))
        self.search_entry.insert(0, "Search product / order / customer…")
        self.search_entry.config(fg="#555e68")
        self.search_entry.bind("<FocusIn>",  self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        self.search_entry.bind("<Return>",   lambda e: self._load(reset=True))

        # Quick filters
        quick_filters = [
            ("market",          "Market"),
            ("customersegment", "Segment"),
            ("deliverystatus",  "Delivery"),
            ("orderstatus",     "Order Status"),
            ("shippingmode",    "Ship Mode"),
        ]
        self._combo_widgets = {}
        for logical, label in quick_filters:
            f = tk.Frame(fb, bg=BG_PANEL)
            f.pack(side="left", padx=5)
            tk.Label(f, text=label, bg=BG_PANEL, fg=TEXT_SECONDARY,
                     font=FONT_SMALL).pack(anchor="w")
            var = tk.StringVar(value="All")
            try:
                vals = ["All"] + fetch_distinct(logical)
            except Exception:
                vals = ["All"]
            cw = self._make_filter_combo(f, var, vals)
            cw.pack()
            self._filter_vars[logical] = var

        tk.Button(fb, text="Apply", bg=ACCENT, fg=BG_DARK, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=lambda: self._load(reset=True)).pack(side="left", padx=(10,4), pady=4)
        tk.Button(fb, text="Reset", bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=self._reset_filters).pack(side="left")
        tk.Button(fb, text="🔄 Refresh", bg=BG_PANEL, fg=ACCENT2, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=lambda: self._load(reset=True)).pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Treeview table
        tree_frame = tk.Frame(self, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=0)

        self._setup_treeview_style()

        self.tree = ttk.Treeview(tree_frame, columns=DISPLAY_HEADERS,
                                  show="headings", style="Records.Treeview",
                                  selectmode="browse")
        for header, width in zip(DISPLAY_HEADERS, COL_WIDTHS):
            self.tree.heading(header, text=header,
                              command=lambda h=header: self._sort_by(h))
            self.tree.column(header, width=width, minwidth=50, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Hover highlight
        self.tree.bind("<Motion>",   self._on_hover)
        self.tree.bind("<Leave>",    lambda e: self._clear_hover())
        self._hover_item = None

        # Pagination bar
        pg = tk.Frame(self, bg=BG_PANEL, padx=20, pady=8)
        pg.pack(fill="x")

        self.page_lbl = tk.Label(pg, text="", bg=BG_PANEL, fg=TEXT_SECONDARY, font=FONT_SMALL)
        self.page_lbl.pack(side="left")

        tk.Button(pg, text="⟪ First",  bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=3,
                  command=lambda: self._load(reset=True)).pack(side="left", padx=3)
        tk.Button(pg, text="‹ Prev",   bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=3,
                  command=self._prev_page).pack(side="left", padx=3)
        tk.Button(pg, text="Next ›",   bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=3,
                  command=self._next_page).pack(side="left", padx=3)
        tk.Button(pg, text="Last ⟫",  bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=3,
                  command=self._last_page).pack(side="left", padx=3)

        self.rows_lbl = tk.Label(pg, text="", bg=BG_PANEL, fg=ACCENT3, font=FONT_SMALL)
        self.rows_lbl.pack(side="right")

        self._load(reset=True)

    # ── Custom styled filter combo ─────────────────────────
    def _make_filter_combo(self, parent, var, options):
        frame = tk.Frame(parent, bg=BG_INPUT, highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=ACCENT, cursor="hand2")
        lbl = tk.Label(frame, textvariable=var, bg=BG_INPUT, fg=TEXT_PRIMARY,
                       font=FONT_SMALL, anchor="w", padx=6, pady=3, width=12)
        lbl.pack(side="left", fill="x", expand=True)
        tk.Label(frame, text="▾", bg=BG_INPUT, fg=ACCENT,
                 font=("Segoe UI", 8), padx=4).pack(side="right")

        popup_ref = [None]

        def show(e=None):
            if popup_ref[0] and popup_ref[0].winfo_exists():
                popup_ref[0].destroy(); return
            pw = tk.Toplevel(frame)
            pw.overrideredirect(True)
            pw.configure(bg=BORDER)
            pw.attributes("-topmost", True)
            popup_ref[0] = pw
            frame.update_idletasks()
            x = frame.winfo_rootx()
            y = frame.winfo_rooty() + frame.winfo_height()
            w = max(frame.winfo_width(), 150)
            pw.geometry(f"{w}x{min(len(options)*26+2, 180)}+{x}+{y}")
            cv = tk.Canvas(pw, bg=BG_INPUT, highlightthickness=0)
            sb = tk.Scrollbar(pw, orient="vertical", command=cv.yview)
            inn = tk.Frame(cv, bg=BG_INPUT)
            inn.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
            cv.create_window((0,0), window=inn, anchor="nw")
            cv.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            cv.pack(fill="both", expand=True)
            for opt in options:
                def pick(o=opt):
                    var.set(o)
                    if pw.winfo_exists(): pw.destroy()
                r = tk.Frame(inn, bg=BG_INPUT, cursor="hand2")
                r.pack(fill="x")
                ol = tk.Label(r, text=opt, bg=BG_INPUT, fg=TEXT_PRIMARY,
                              font=FONT_SMALL, anchor="w", padx=8, pady=4)
                ol.pack(fill="x")
                ol.bind("<Button-1>", lambda e, p=pick: p())
                r.bind("<Button-1>",  lambda e, p=pick: p())
                ol.bind("<Enter>", lambda e, row=r, la=ol: (row.config(bg=BG_HOVER), la.config(bg=BG_HOVER)))
                ol.bind("<Leave>", lambda e, row=r, la=ol: (row.config(bg=BG_INPUT), la.config(bg=BG_INPUT)))
            pw.bind("<FocusOut>", lambda e: pw.destroy() if pw.winfo_exists() else None)
            pw.focus_set()

        frame.bind("<Button-1>", show)
        lbl.bind("<Button-1>", show)
        return frame

    # ── Treeview style ────────────────────────────────────
    def _setup_treeview_style(self):
        s = ttk.Style()
        s.theme_use("default")
        s.configure("Records.Treeview",
                    background=BG_CARD, foreground=TEXT_PRIMARY,
                    fieldbackground=BG_CARD, rowheight=26,
                    font=("Segoe UI", 9), borderwidth=0)
        s.configure("Records.Treeview.Heading",
                    background=BG_PANEL, foreground=ACCENT,
                    font=("Segoe UI", 9, "bold"), relief="flat",
                    borderwidth=0, padding=6)
        s.map("Records.Treeview",
              background=[("selected", BG_HOVER)],
              foreground=[("selected", ACCENT)])
        s.map("Records.Treeview.Heading",
              background=[("active", BG_HOVER)])

    # ── Data loading ──────────────────────────────────────
    def _build_query(self, count_only=False):
        # Resolve real column names
        try:
            real_cols = [col(c) for c in DISPLAY_COLS]
        except Exception:
            real_cols = DISPLAY_COLS

        search = self._search_var.get().strip()
        if search in ("Search product / order / customer…", ""):
            search = ""

        params = []
        where  = "WHERE 1=1"

        # Filter dropdowns
        for logical, var in self._filter_vars.items():
            val = var.get()
            if val and val != "All":
                try:
                    c = col(logical)
                    where += f" AND [{c}] = ?"
                    params.append(val)
                except Exception:
                    pass

        # Search across key text columns
        if search:
            try:
                sc_cols = [col("productname"), col("orderid"),
                           col("customerfname"), col("customerlname")]
                like_parts = " OR ".join(f"CAST([{c}] AS NVARCHAR(MAX)) LIKE ?" for c in sc_cols)
                where += f" AND ({like_parts})"
                params.extend([f"%{search}%"] * len(sc_cols))
            except Exception:
                pass

        if count_only:
            return f"SELECT COUNT(*) FROM supplychain {where}", params

        sel = ", ".join(f"[{c}]" for c in real_cols)
        return (f"SELECT {sel} FROM supplychain {where} "
                f"ORDER BY (SELECT NULL) OFFSET {self._offset} ROWS FETCH NEXT {PAGE_SIZE} ROWS ONLY"), params

    def _load(self, reset=False):
        if reset:
            self._offset = 0

        # Total count
        try:
            cq, cp = self._build_query(count_only=True)
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(cq, cp)
            self._total = cur.fetchone()[0]
            conn.close()
        except Exception as e:
            self._total = 0

        # Data rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            dq, dp = self._build_query()
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(dq, dp)
            rows = cur.fetchall()
            conn.close()

            for i, row in enumerate(rows):
                vals = []
                for v in row:
                    if v is None:
                        vals.append("")
                    elif isinstance(v, float):
                        vals.append(f"{v:,.2f}")
                    else:
                        vals.append(str(v))
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", "end", values=vals, tags=(tag,))

            self.tree.tag_configure("even", background=BG_CARD)
            self.tree.tag_configure("odd",  background=BG_PANEL)

        except Exception as e:
            self.tree.insert("", "end", values=[f"Error: {e}"] + [""]*(len(DISPLAY_HEADERS)-1))

        # Update labels
        page     = self._offset // PAGE_SIZE + 1
        total_pg = max(1, (self._total + PAGE_SIZE - 1) // PAGE_SIZE)
        showing  = min(self._offset + PAGE_SIZE, self._total)
        self.page_lbl.config(text=f"Page {page} of {total_pg}")
        self.rows_lbl.config(text=f"Showing {self._offset+1}–{showing} of {self._total:,} records")

        try:
            n = get_total_records()
            self.count_lbl.config(text=f"📦 Total in DB: {n:,}", fg=ACCENT3)
        except Exception:
            pass

    # ── Pagination ────────────────────────────────────────
    def _prev_page(self):
        if self._offset >= PAGE_SIZE:
            self._offset -= PAGE_SIZE
            self._load()

    def _next_page(self):
        if self._offset + PAGE_SIZE < self._total:
            self._offset += PAGE_SIZE
            self._load()

    def _last_page(self):
        pages = (self._total - 1) // PAGE_SIZE
        self._offset = pages * PAGE_SIZE
        self._load()

    def _reset_filters(self):
        for v in self._filter_vars.values():
            v.set("All")
        self._search_var.set("")
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, "Search product / order / customer…")
        self.search_entry.config(fg="#555e68")
        self._load(reset=True)

    # ── Hover highlight ───────────────────────────────────
    def _on_hover(self, event):
        item = self.tree.identify_row(event.y)
        if item != self._hover_item:
            if self._hover_item:
                tags = self.tree.item(self._hover_item, "tags")
                bg = BG_CARD if "even" in tags else BG_PANEL
                self.tree.tag_configure(self._hover_item+"_hover", background=bg)
            self._hover_item = item

    def _clear_hover(self):
        self._hover_item = None

    # ── Sort ──────────────────────────────────────────────
    def _sort_by(self, header):
        items = [(self.tree.set(k, header), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda x: float(x[0].replace(",","")) if x[0] else 0)
        except ValueError:
            items.sort(key=lambda x: x[0].lower())
        for i, (_, k) in enumerate(items):
            self.tree.move(k, "", i)
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.item(k, tags=(tag,))

    # ── Search helpers ────────────────────────────────────
    def _search_focus_in(self, e):
        if self.search_entry.get() == "Search product / order / customer…":
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=TEXT_PRIMARY)

    def _search_focus_out(self, e):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search product / order / customer…")
            self.search_entry.config(fg="#555e68")

    def refresh(self):
        self._load(reset=True)
