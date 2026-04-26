# Supply Chain Analytics Suite

A full-featured desktop analytics application built with Python (Tkinter) and SQL Server.

## Prerequisites

- Python 3.8+
- SQL Server Express (`.\SQLEXPRESS`)
- ODBC Driver 17 for SQL Server
- Database: `SupplyChain` with table `supplychain`

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
cd SupplyChainApp
python main.py
```

## Project Structure

```
SupplyChainApp/
├── main.py                     # Application entry point & root window
├── requirements.txt
├── utils/
│   ├── db.py                   # All SQL Server queries & connection logic
│   └── theme.py                # Colors, fonts, spacing constants
├── components/
│   ├── sidebar.py              # Left navigation sidebar
│   └── widgets.py              # Reusable UI components (buttons, cards, etc.)
└── pages/
    ├── home_page.py            # Home dashboard with live stats
    ├── about_page.py           # About page with column documentation
    ├── auth_page.py            # Sign In / Register / Logout
    ├── add_record_page.py      # Full data entry form (all 46 columns)
    └── analysis_page.py        # Analytics with 5 KPIs + 9 charts + filters
```

## Features

### Pages
- **Home** — Live stats overview, feature highlights, KPI cards
- **Analysis** — 6 filter dropdowns (Market, Segment, Ship Mode, Order Status, Delivery, Department) + 5 KPI cards + 9 charts
- **Add Record** — Data entry form for all 46 supply chain columns, saves to SQL Server
- **About** — Column reference, tech stack documentation
- **Auth** — Sign In / Register (hashed passwords stored in `app_users` table)

### Charts in Analysis Page
1. Sales by Category (horizontal bar)
2. Delivery Status Distribution (pie)
3. Monthly Sales Trend (line + fill)
4. Shipping Mode Breakdown (donut)
5. Profit by Customer Segment (bar)
6. Sales by Market (bar with value labels)
7. Top Regions by Profit (horizontal bar)
8. Monthly Profit Trend (bar)
9. Top 10 Products by Sales (horizontal bar)

## SQL Server Setup

Ensure your SQL Server has:
- Server: `.\SQLEXPRESS`
- Database: `SupplyChain`
- Table: `supplychain` with all columns matching the dataset

The app auto-creates an `app_users` table for authentication on first run.
