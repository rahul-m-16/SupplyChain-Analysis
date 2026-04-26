import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker
import matplotlib.patches as mpatches
import numpy as np

from utils.theme import *
from utils.db import (
    fetch_kpis, fetch_distinct, fetch_aggregated,
    fetch_time_series, fetch_delivery_status_dist,
    fetch_shipping_mode_dist, fetch_segment_profit,
    fetch_market_sales, fetch_late_delivery_by_market,
    fetch_discount_vs_profit, fetch_order_status_dist,
    fetch_dept_sales
)
from components.widgets import kpi_card, scrollable_frame

matplotlib.rcParams.update({
    'axes.facecolor':  BG_CARD,
    'figure.facecolor': BG_DARK,
    'axes.edgecolor':  BORDER,
    'axes.labelcolor': TEXT_SECONDARY,
    'xtick.color':     TEXT_SECONDARY,
    'ytick.color':     TEXT_SECONDARY,
    'text.color':      TEXT_PRIMARY,
    'grid.color':      BORDER,
    'grid.alpha':      0.35,
    'font.family':     'Segoe UI',
    'font.size':       8,
})

CC = CHART_COLORS   # shorthand


def _chart_frame(parent, title, side=None, expand=True, padx=(0,0), w=None, h=None):
    outer = tk.Frame(parent, bg=BG_CARD)
    if side:
        outer.pack(side=side, fill="both", expand=expand, padx=padx)
    bar = tk.Frame(outer, bg=ACCENT, width=4)
    bar.pack(side="left", fill="y")
    inner = tk.Frame(outer, bg=BG_CARD)
    inner.pack(side="left", fill="both", expand=True)
    tk.Label(inner, text=title, bg=BG_CARD, fg=TEXT_PRIMARY,
             font=("Segoe UI", 10, "bold"), padx=10, pady=6).pack(anchor="w")
    return outer, inner


def _embed(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=(0, 8))
    return canvas


def _row(parent, pady=6):
    f = tk.Frame(parent, bg=BG_DARK, padx=20, pady=pady)
    f.pack(fill="x")
    return f


class AnalysisPage(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.app_ref = app_ref
        self.filter_vars = {}
        self._build()

    def _build(self):
        # ── Top bar ──────────────────────────────────────────
        top = tk.Frame(self, bg=BG_DARK, padx=20, pady=14)
        top.pack(fill="x")
        tk.Label(top, text="Supply Chain Analysis", bg=BG_DARK,
                 fg=ACCENT, font=FONT_HEADING).pack(side="left")
        tk.Button(top, text="🔄  Refresh", bg=ACCENT2, fg="#fff",
                  font=FONT_BTN, relief="flat", cursor="hand2",
                  padx=14, pady=6, command=self.refresh).pack(side="right")

        # ── Filter bar ───────────────────────────────────────
        fb = tk.Frame(self, bg=BG_PANEL, padx=20, pady=8)
        fb.pack(fill="x")
        tk.Label(fb, text="FILTERS:", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))

        filter_cols = [
            ("market",          "Market"),
            ("customersegment", "Segment"),
            ("shippingmode",    "Ship Mode"),
            ("orderstatus",     "Order Status"),
            ("deliverystatus",  "Delivery"),
            ("departmentname",  "Department"),
        ]
        style = ttk.Style()
        style.configure("F.TCombobox", fieldbackground=BG_INPUT,
                        background=BG_INPUT, foreground=TEXT_PRIMARY, arrowcolor=ACCENT)
        for logical, label in filter_cols:
            f = tk.Frame(fb, bg=BG_PANEL)
            f.pack(side="left", padx=5)
            tk.Label(f, text=label, bg=BG_PANEL, fg=TEXT_SECONDARY,
                     font=FONT_SMALL).pack(anchor="w")
            var = tk.StringVar(value="All")
            try:
                vals = ["All"] + fetch_distinct(logical)
            except Exception:
                vals = ["All"]
            combo = ttk.Combobox(f, textvariable=var, values=vals,
                                 style="F.TCombobox", width=13, state="readonly")
            combo.pack()
            self.filter_vars[logical] = var

        tk.Button(fb, text="Apply", bg=ACCENT, fg=BG_DARK, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._apply).pack(side="left", padx=(10, 4), pady=4)
        tk.Button(fb, text="Reset", bg=BG_HOVER, fg=TEXT_PRIMARY, font=FONT_BTN,
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=self._reset).pack(side="left")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Scrollable content ───────────────────────────────
        sc, self.sf = scrollable_frame(self)
        sc.pack(fill="both", expand=True)
        self._build_content()

    def _filters(self):
        return {k: v.get() for k, v in self.filter_vars.items()}

    def _apply(self):
        self._clear(); self._build_content()

    def _reset(self):
        for v in self.filter_vars.values():
            v.set("All")
        self._clear(); self._build_content()

    def _clear(self):
        for w in self.sf.winfo_children():
            w.destroy()

    def refresh(self):
        self._clear(); self._build_content()

    # ── Content builder ──────────────────────────────────────
    def _build_content(self):
        sf   = self.sf
        flt  = self._filters()

        # ── KPI Cards ────────────────────────────────────────
        kpi_sec = tk.Frame(sf, bg=BG_DARK, padx=20, pady=12)
        kpi_sec.pack(fill="x")
        tk.Label(kpi_sec, text="KEY PERFORMANCE INDICATORS", bg=BG_DARK,
                 fg=TEXT_MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))
        krow = tk.Frame(kpi_sec, bg=BG_DARK)
        krow.pack(fill="x")
        try:
            k = fetch_kpis()
            kdata = [
                ("Total Orders",    f"{int(k['total_orders']):,}",      ACCENT,  "📦"),
                ("Total Sales",     f"${k['total_sales']:,.0f}",         ACCENT3, "💰"),
                ("Total Profit",    f"${k['total_profit']:,.0f}",        ACCENT4, "📈"),
                ("Late Delivery %", f"{k['late_delivery_pct']}%",        DANGER,  "⚠️"),
                ("Avg Ship Days",   f"{k['avg_shipping_days']:.1f} days", ACCENT2, "🚚"),
            ]
        except Exception as e:
            kdata = [("Error", str(e)[:40], DANGER, "❌")]
        for i, (title, val, color, icon) in enumerate(kdata):
            c = kpi_card(krow, title, val, color, icon)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            krow.columnconfigure(i, weight=1)

        tk.Frame(sf, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)

        # ══ ROW 1 — Sales by Category (H-Bar)  +  Delivery Status (Pie) ══════
        r1 = _row(sf)

        # Chart 1 — Horizontal Bar: Sales by Category
        f1, i1 = _chart_frame(r1, "📊  Sales by Category (Top 10)", side="left", expand=True, padx=(0, 6))
        try:
            labels, vals = fetch_aggregated("categoryname", "sales", filters=flt)
            fig = Figure(figsize=(5.8, 3.4), dpi=88)
            ax  = fig.add_subplot(111)
            y   = range(len(labels))
            colors = CC[:len(labels)]
            bars = ax.barh(list(y), vals, color=colors[::-1] if colors else colors, height=0.6)
            ax.set_yticks(list(y))
            ax.set_yticklabels([l[:22] for l in labels[::-1]], fontsize=7)
            ax.set_xlabel("Sales ($)")
            ax.grid(axis='x', alpha=0.3)
            for spine in ['top','right']: ax.spines[spine].set_visible(False)
            fig.tight_layout()
            _embed(fig, i1)
        except Exception as e:
            tk.Label(i1, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=400).pack(padx=8, pady=8)

        # Chart 2 — Donut: Delivery Status
        f2, i2 = _chart_frame(r1, "🍩  Delivery Status", side="left", expand=False, padx=(0, 0))
        f2.config(width=310)
        try:
            labs, vals2 = fetch_delivery_status_dist(flt)
            fig2 = Figure(figsize=(3.4, 3.4), dpi=88)
            ax2  = fig2.add_subplot(111)
            wedges, _, autos = ax2.pie(
                vals2, labels=None, colors=CC[:len(labs)],
                autopct='%1.0f%%', startangle=90,
                wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2),
                pctdistance=0.75
            )
            for a in autos: a.set_fontsize(7); a.set_color('#fff')
            ax2.legend(wedges, [l[:18] for l in labs], loc="lower center",
                       bbox_to_anchor=(0.5,-0.08), ncol=2, fontsize=6,
                       framealpha=0, labelcolor=TEXT_SECONDARY)
            fig2.tight_layout()
            _embed(fig2, i2)
        except Exception as e:
            tk.Label(i2, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=280).pack(padx=8, pady=8)

        # ══ ROW 2 — Monthly Sales Trend (Area) + Shipping Mode (Pie) ══════════
        r2 = _row(sf)

        # Chart 3 — Area: Monthly Sales Trend
        f3, i3 = _chart_frame(r2, "📈  Monthly Sales Trend", side="left", expand=True, padx=(0, 6))
        try:
            # key: orderdatedateorders  (order_date_(DateOrders) stripped)
            tl, tv = fetch_time_series("orderdatedateorders", "sales", flt)
            fig3 = Figure(figsize=(5.8, 3.2), dpi=88)
            ax3  = fig3.add_subplot(111)
            x    = range(len(tl))
            ax3.fill_between(x, tv, alpha=0.25, color=ACCENT)
            ax3.plot(x, tv, color=ACCENT, linewidth=2, marker='o', markersize=3)
            step = max(1, len(tl) // 9)
            ax3.set_xticks(list(x)[::step])
            ax3.set_xticklabels(tl[::step], rotation=35, ha='right', fontsize=7)
            ax3.set_ylabel("Sales ($)")
            ax3.grid(True, alpha=0.25)
            for spine in ['top','right']: ax3.spines[spine].set_visible(False)
            fig3.tight_layout()
            _embed(fig3, i3)
        except Exception as e:
            tk.Label(i3, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=400).pack(padx=8, pady=8)

        # Chart 4 — Pie: Shipping Mode
        f4, i4 = _chart_frame(r2, "🚢  Shipping Mode Mix", side="left", expand=False, padx=(0, 0))
        f4.config(width=310)
        try:
            sl, sv = fetch_shipping_mode_dist(flt)
            fig4 = Figure(figsize=(3.4, 3.2), dpi=88)
            ax4  = fig4.add_subplot(111)
            wedges4, _, auto4 = ax4.pie(
                sv, labels=None, colors=CC[:len(sl)],
                autopct='%1.1f%%', startangle=140,
                pctdistance=0.72,
                wedgeprops=dict(edgecolor=BG_DARK, linewidth=2)
            )
            for a in auto4: a.set_fontsize(7); a.set_color('#fff')
            ax4.legend(wedges4, sl, loc="lower center", bbox_to_anchor=(0.5,-0.08),
                       ncol=2, fontsize=6, framealpha=0, labelcolor=TEXT_SECONDARY)
            fig4.tight_layout()
            _embed(fig4, i4)
        except Exception as e:
            tk.Label(i4, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=280).pack(padx=8, pady=8)

        # ══ ROW 3 — Profit by Segment (Grouped Bar) + Market Sales (Bar) ══════
        r3 = _row(sf)

        # Chart 5 — Bar: Profit by Customer Segment
        f5, i5 = _chart_frame(r3, "👥  Profit by Customer Segment", side="left", expand=True, padx=(0, 6))
        try:
            seg_l, seg_v = fetch_segment_profit(flt)
            fig5 = Figure(figsize=(4.4, 3.0), dpi=88)
            ax5  = fig5.add_subplot(111)
            bar_c = [ACCENT3 if v >= 0 else DANGER for v in seg_v]
            x5 = range(len(seg_l))
            b5 = ax5.bar(x5, seg_v, color=bar_c, width=0.5, edgecolor=BG_DARK)
            ax5.set_xticks(list(x5))
            ax5.set_xticklabels(seg_l, fontsize=8)
            ax5.set_ylabel("Profit ($)")
            ax5.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda x, _: f"${x/1e6:.1f}M"))
            ax5.grid(axis='y', alpha=0.3)
            for bar, val in zip(b5, seg_v):
                ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                         f"${val/1e6:.2f}M", ha='center', fontsize=7, color=TEXT_SECONDARY)
            for spine in ['top','right']: ax5.spines[spine].set_visible(False)
            fig5.tight_layout()
            _embed(fig5, i5)
        except Exception as e:
            tk.Label(i5, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=380).pack(padx=8, pady=8)

        # Chart 6 — Horizontal Bar: Market Sales
        f6, i6 = _chart_frame(r3, "🌍  Sales by Market", side="left", expand=True, padx=(0, 0))
        try:
            ml, mv = fetch_market_sales(flt)
            fig6 = Figure(figsize=(4.4, 3.0), dpi=88)
            ax6  = fig6.add_subplot(111)
            y6 = range(len(ml))
            b6 = ax6.barh(list(y6), mv, color=CC[:len(ml)], height=0.55)
            ax6.set_yticks(list(y6))
            ax6.set_yticklabels(ml, fontsize=8)
            ax6.set_xlabel("Sales ($)")
            ax6.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda x, _: f"${x/1e6:.0f}M"))
            for bar, val in zip(b6, mv):
                ax6.text(bar.get_width()*1.01, bar.get_y()+bar.get_height()/2,
                         f"${val/1e6:.1f}M", va='center', fontsize=7, color=TEXT_SECONDARY)
            ax6.grid(axis='x', alpha=0.3)
            for spine in ['top','right']: ax6.spines[spine].set_visible(False)
            fig6.tight_layout()
            _embed(fig6, i6)
        except Exception as e:
            tk.Label(i6, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=380).pack(padx=8, pady=8)

        # ══ ROW 4 — Monthly Profit Trend (Bar) + Order Status (Horizontal Bar) ═
        r4 = _row(sf)

        # Chart 7 — Bar: Monthly Profit Trend
        f7, i7 = _chart_frame(r4, "📉  Monthly Profit Trend", side="left", expand=True, padx=(0, 6))
        try:
            pt_l, pt_v = fetch_time_series("orderdatedateorders", "orderprofitperorder", flt)
            fig7 = Figure(figsize=(5.8, 3.2), dpi=88)
            ax7  = fig7.add_subplot(111)
            col7 = [ACCENT3 if v >= 0 else DANGER for v in pt_v]
            ax7.bar(range(len(pt_l)), pt_v, color=col7, width=0.75)
            step7 = max(1, len(pt_l) // 9)
            ax7.set_xticks(list(range(0, len(pt_l), step7)))
            ax7.set_xticklabels(pt_l[::step7], rotation=35, ha='right', fontsize=7)
            ax7.set_ylabel("Profit ($)")
            ax7.axhline(0, color=BORDER, linewidth=0.8)
            ax7.grid(axis='y', alpha=0.25)
            for spine in ['top','right']: ax7.spines[spine].set_visible(False)
            fig7.tight_layout()
            _embed(fig7, i7)
        except Exception as e:
            tk.Label(i7, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=400).pack(padx=8, pady=8)

        # Chart 8 — H-Bar: Order Status Distribution
        f8, i8 = _chart_frame(r4, "📋  Order Status Distribution", side="left", expand=False, padx=(0, 0))
        f8.config(width=310)
        try:
            osl, osv = fetch_order_status_dist(flt)
            fig8 = Figure(figsize=(3.4, 3.2), dpi=88)
            ax8  = fig8.add_subplot(111)
            y8 = range(len(osl))
            ax8.barh(list(y8), osv, color=CC[:len(osl)], height=0.55)
            ax8.set_yticks(list(y8))
            ax8.set_yticklabels([l[:16] for l in osl], fontsize=7)
            ax8.set_xlabel("Orders")
            ax8.grid(axis='x', alpha=0.3)
            for spine in ['top','right']: ax8.spines[spine].set_visible(False)
            fig8.tight_layout()
            _embed(fig8, i8)
        except Exception as e:
            tk.Label(i8, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=280).pack(padx=8, pady=8)

        # ══ ROW 5 — Late Delivery % by Market (Bar) + Dept Sales (Pie) ══════════
        r5 = _row(sf)

        # Chart 9 — Bar: Late Delivery Risk % by Market
        f9, i9 = _chart_frame(r5, "⚠️  Late Delivery Risk % by Market", side="left", expand=True, padx=(0, 6))
        try:
            ldl, ldv = fetch_late_delivery_by_market(flt)
            fig9 = Figure(figsize=(5.4, 3.0), dpi=88)
            ax9  = fig9.add_subplot(111)
            col9 = [DANGER if v > 50 else WARNING if v > 30 else ACCENT3 for v in ldv]
            b9 = ax9.bar(range(len(ldl)), ldv, color=col9, width=0.55)
            ax9.set_xticks(range(len(ldl)))
            ax9.set_xticklabels(ldl, rotation=15, ha='right', fontsize=8)
            ax9.set_ylabel("Late Delivery %")
            ax9.set_ylim(0, 105)
            for bar, val in zip(b9, ldv):
                ax9.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
                         f"{val:.0f}%", ha='center', fontsize=7, color=TEXT_SECONDARY)
            ax9.grid(axis='y', alpha=0.25)
            for spine in ['top','right']: ax9.spines[spine].set_visible(False)
            fig9.tight_layout()
            _embed(fig9, i9)
        except Exception as e:
            tk.Label(i9, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=400).pack(padx=8, pady=8)

        # Chart 10 — Pie: Sales by Department
        f10, i10 = _chart_frame(r5, "🏬  Sales by Department", side="left", expand=False, padx=(0, 0))
        f10.config(width=310)
        try:
            dpl, dpv = fetch_dept_sales(flt)
            fig10 = Figure(figsize=(3.4, 3.0), dpi=88)
            ax10  = fig10.add_subplot(111)
            wedges10, _, auto10 = ax10.pie(
                dpv, labels=None, colors=CC[:len(dpl)],
                autopct='%1.0f%%', startangle=90,
                wedgeprops=dict(edgecolor=BG_DARK, linewidth=2),
                pctdistance=0.75
            )
            for a in auto10: a.set_fontsize(7); a.set_color('#fff')
            ax10.legend(wedges10, [l[:14] for l in dpl], loc="lower center",
                        bbox_to_anchor=(0.5,-0.08), ncol=2, fontsize=6,
                        framealpha=0, labelcolor=TEXT_SECONDARY)
            fig10.tight_layout()
            _embed(fig10, i10)
        except Exception as e:
            tk.Label(i10, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=280).pack(padx=8, pady=8)

        # ══ ROW 6 — Scatter: Discount Rate vs Profit + Top Products ═════════════
        r6 = _row(sf)

        # Chart 11 — Scatter: Discount vs Profit
        f11, i11 = _chart_frame(r6, "🔵  Discount Rate vs. Order Profit (Scatter)", side="left", expand=True, padx=(0, 6))
        try:
            dx, dy = fetch_discount_vs_profit(flt)
            fig11 = Figure(figsize=(5.4, 3.2), dpi=88)
            ax11  = fig11.add_subplot(111)
            colors11 = [ACCENT3 if v >= 0 else DANGER for v in dy]
            ax11.scatter(dx, dy, c=colors11, alpha=0.45, s=14, linewidths=0)
            ax11.axhline(0, color=BORDER, linewidth=0.8, linestyle='--')
            ax11.set_xlabel("Discount Rate")
            ax11.set_ylabel("Profit ($)")
            ax11.grid(True, alpha=0.2)
            for spine in ['top','right']: ax11.spines[spine].set_visible(False)
            # trend line
            if len(dx) > 5:
                z = np.polyfit(dx, dy, 1)
                p = np.poly1d(z)
                xs = sorted(dx)
                ax11.plot(xs, [p(x) for x in xs], color=ACCENT2, linewidth=1.5,
                          linestyle='--', alpha=0.8, label='Trend')
                ax11.legend(fontsize=7, framealpha=0)
            fig11.tight_layout()
            _embed(fig11, i11)
        except Exception as e:
            tk.Label(i11, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=400).pack(padx=8, pady=8)

        # ══ ROW 7 — Full width: Top 10 Products ════════════════════════════════
        r7 = _row(sf)
        f12, i12 = _chart_frame(r7, "🏆  Top 10 Products by Sales", side="left", expand=True)
        try:
            pl, pv = fetch_aggregated("productname", "sales", filters=flt, limit=10)
            fig12 = Figure(figsize=(12, 3.6), dpi=88)
            ax12  = fig12.add_subplot(111)
            short = [l[:38]+"…" if len(l) > 38 else l for l in pl]
            y12 = range(len(short))
            ax12.barh(list(y12), pv, color=CC[:len(pl)], height=0.6)
            ax12.set_yticks(list(y12))
            ax12.set_yticklabels(short[::-1], fontsize=7)
            ax12.set_xlabel("Sales ($)")
            ax12.grid(axis='x', alpha=0.25)
            for spine in ['top','right']: ax12.spines[spine].set_visible(False)
            fig12.tight_layout()
            _embed(fig12, i12)
        except Exception as e:
            tk.Label(i12, text=f"Error: {e}", bg=BG_CARD, fg=DANGER, font=FONT_SMALL, wraplength=900).pack(padx=8, pady=8)

        tk.Frame(sf, bg=BG_DARK, height=24).pack()
