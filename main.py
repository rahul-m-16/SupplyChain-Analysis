import tkinter as tk
from tkinter import messagebox

from utils.theme import *
from utils.db import init_db
from components.sidebar import Sidebar
from pages.home_page import HomePage
from pages.about_page import AboutPage
from pages.auth_page import AuthPage
from pages.add_record_page import AddRecordPage
from pages.analysis_page import AnalysisPage
from pages.records_page import RecordsPage


class SupplyChainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supply Chain Analytics Suite")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg=BG_DARK)
        self.current_user = None

        try:
            init_db()
        except Exception as e:
            messagebox.showerror("DB Error",
                f"Cannot connect to SQL Server.\n\n{e}\n\n"
                "Ensure SQL Server Express is running at .\\SQLEXPRESS\n"
                "and the database 'SupplyChain' exists.")

        self._build_layout()
        self.navigate("home")

    def _build_layout(self):
        self.sidebar = Sidebar(self, on_navigate=self.navigate, app_ref=self)
        self.sidebar.pack(side="left", fill="y")

        # Right content area
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        # Pages dict - lazily created
        self.pages = {}

    def _get_page(self, name):
        if name not in self.pages:
            page_map = {
                "home": HomePage,
                "about": AboutPage,
                "signin": AuthPage,
                "add_record": AddRecordPage,
                "records":    RecordsPage,
                "analysis": AnalysisPage,
            }
            cls = page_map.get(name)
            if cls:
                page = cls(self.content, app_ref=self)
                page.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.pages[name] = page
        return self.pages.get(name)

    def navigate(self, page_name):
        # Hide all pages
        for page in self.pages.values():
            page.place_forget()

        page = self._get_page(page_name)
        if page:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            page.tkraise()
            # Update sidebar active state
            if page_name in ["home", "about", "analysis", "add_record", "records"]:
                self.sidebar.set_active(page_name)

        # Refresh home stats when navigating there
        if page_name == "home" and hasattr(page, "refresh"):
            page.refresh()

    def set_user(self, user_info):
        self.current_user = user_info
        self.sidebar.update_user(user_info["username"])

    def logout(self):
        self.current_user = None
        self.sidebar.update_user(None)
        self.navigate("home")
        from components.widgets import toast
        toast(self, "Signed out successfully.", INFO)


if __name__ == "__main__":
    app = SupplyChainApp()
    app.mainloop()
