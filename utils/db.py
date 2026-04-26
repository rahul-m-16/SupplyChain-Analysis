import pyodbc
import hashlib
import re

SERVER = r'.\SQLEXPRESS'
DATABASE = 'SupplyChain'
CONN_STR = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SERVER};'
    f'DATABASE={DATABASE};'
    f'Trusted_Connection=yes;'
)

_COL_CACHE = {}


def get_connection():
    return pyodbc.connect(CONN_STR)


def _load_columns():
    global _COL_CACHE
    if _COL_CACHE:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT TOP 0 * FROM supplychain")
    real_cols = [d[0] for d in cur.description]
    conn.close()
    _COL_CACHE = {re.sub(r'[^a-z0-9]', '', c.lower()): c for c in real_cols}


def col(name):
    _load_columns()
    key = re.sub(r'[^a-z0-9]', '', name.lower())
    if key not in _COL_CACHE:
        raise KeyError(f"Column not found: '{name}' (key='{key}')\nAvailable: {sorted(_COL_CACHE.keys())}")
    return _COL_CACHE[key]


def _fc(filters):
    clause, params = "", []
    if filters:
        for logical, val in filters.items():
            if val and val != "All":
                try:
                    clause += f" AND [{col(logical)}] = ?"
                    params.append(val)
                except KeyError:
                    pass
    return clause, params


# ── Auth ───────────────────────────────────────────────────────────────────────
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='app_users' AND xtype='U')
        CREATE TABLE app_users (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            username      NVARCHAR(100) UNIQUE NOT NULL,
            email         NVARCHAR(200) UNIQUE NOT NULL,
            password_hash NVARCHAR(256) NOT NULL,
            created_at    DATETIME DEFAULT GETDATE()
        )
    """)
    conn.commit()
    conn.close()


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO app_users (username,email,password_hash) VALUES (?,?,?)",
            (username, email, _hash(password))
        )
        conn.commit()
        return True, "Registered successfully!"
    except pyodbc.IntegrityError:
        return False, "Username or email already exists."
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id,username FROM app_users WHERE username=? AND password_hash=?",
        (username, _hash(password))
    )
    row = cur.fetchone()
    conn.close()
    return (True, {"id": row[0], "username": row[1]}) if row else (False, "Invalid credentials.")


# ── Supply-chain queries ───────────────────────────────────────────────────────
def get_total_records():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM supplychain")
    n = cur.fetchone()[0]
    conn.close()
    return n


def insert_record(data: dict):
    """Insert a row. Keys are logical names resolved to real SQL column names via col()."""
    _load_columns()
    resolved = {}
    for logical_key, val in data.items():
        try:
            resolved[col(logical_key)] = val
        except KeyError:
            pass  # skip unknown column names silently

    if not resolved:
        raise ValueError(f"No valid columns could be resolved from keys: {list(data.keys())}")

    conn = get_connection()
    cur  = conn.cursor()
    cols_sql = ', '.join(f'[{k}]' for k in resolved)
    ph       = ', '.join('?' for _ in resolved)
    cur.execute(f"INSERT INTO supplychain ({cols_sql}) VALUES ({ph})", list(resolved.values()))
    conn.commit()
    conn.close()


def fetch_distinct(logical_col):
    c = col(logical_col)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT [{c}] FROM supplychain WHERE [{c}] IS NOT NULL ORDER BY [{c}]")
    vals = [r[0] for r in cur.fetchall()]
    conn.close()
    return vals


def fetch_kpis():
    c_sales  = col("sales")
    c_profit = col("orderprofitperorder")
    c_days   = col("daysforshippingreal")
    c_late   = col("latedeliveryrisk")
    c_oid    = col("orderid")

    conn = get_connection()
    cur = conn.cursor()
    results = {}
    for key, sql in [
        ("total_sales",       f"SELECT SUM([{c_sales}]) FROM supplychain"),
        ("total_profit",      f"SELECT SUM([{c_profit}]) FROM supplychain"),
        ("avg_shipping_days", f"SELECT AVG(CAST([{c_days}] AS FLOAT)) FROM supplychain"),
        ("late_delivery_pct", f"SELECT CAST(SUM(CAST([{c_late}] AS INT))*100.0/COUNT(*) AS DECIMAL(5,2)) FROM supplychain"),
        ("total_orders",      f"SELECT COUNT(DISTINCT [{c_oid}]) FROM supplychain"),
    ]:
        cur.execute(sql)
        results[key] = cur.fetchone()[0] or 0
    conn.close()
    return results


def fetch_aggregated(group_logical, agg_logical, agg_func="SUM", filters=None, limit=10):
    g = col(group_logical)
    a = col(agg_logical)
    fclause, params = _fc(filters)
    sql = (f"SELECT TOP {limit} [{g}], {agg_func}([{a}]) as val "
           f"FROM supplychain WHERE 1=1{fclause} "
           f"GROUP BY [{g}] HAVING {agg_func}([{a}]) IS NOT NULL ORDER BY val DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [float(r[1]) for r in rows]


def fetch_time_series(date_logical, value_logical, filters=None):
    # date column key in the actual table is 'orderdatedateorders'
    d = col(date_logical)
    v = col(value_logical)
    fclause, params = _fc(filters)
    sql = (f"SELECT YEAR([{d}]), MONTH([{d}]), SUM([{v}]) "
           f"FROM supplychain WHERE [{d}] IS NOT NULL{fclause} "
           f"GROUP BY YEAR([{d}]), MONTH([{d}]) ORDER BY 1,2")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    labels = [f"{r[0]}-{str(r[1]).zfill(2)}" for r in rows]
    vals   = [float(r[2]) for r in rows]
    return labels, vals


def fetch_delivery_status_dist(filters=None):
    c = col("deliverystatus")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{c}], COUNT(*) FROM supplychain "
           f"WHERE [{c}] IS NOT NULL{fclause} GROUP BY [{c}]")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [r[1] for r in rows]


def fetch_shipping_mode_dist(filters=None):
    c = col("shippingmode")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{c}], COUNT(*) FROM supplychain "
           f"WHERE [{c}] IS NOT NULL{fclause} GROUP BY [{c}]")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [r[1] for r in rows]


def fetch_segment_profit(filters=None):
    cs = col("customersegment")
    cp = col("orderprofitperorder")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{cs}], SUM([{cp}]) FROM supplychain "
           f"WHERE 1=1{fclause} GROUP BY [{cs}] ORDER BY 2 DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [float(r[1]) for r in rows]


def fetch_market_sales(filters=None):
    cm = col("market")
    cs = col("sales")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{cm}], SUM([{cs}]) FROM supplychain "
           f"WHERE 1=1{fclause} GROUP BY [{cm}] ORDER BY 2 DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [float(r[1]) for r in rows]


def fetch_late_delivery_by_market(filters=None):
    cm = col("market")
    cl = col("latedeliveryrisk")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{cm}], "
           f"SUM(CAST([{cl}] AS INT))*100.0/COUNT(*) as pct "
           f"FROM supplychain WHERE 1=1{fclause} "
           f"GROUP BY [{cm}] ORDER BY pct DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [float(r[1]) for r in rows]


def fetch_discount_vs_profit(filters=None):
    cd = col("orderitemdiscountrate")
    cp = col("orderprofitperorder")
    fclause, params = _fc(filters)
    sql = (f"SELECT TOP 500 [{cd}], [{cp}] FROM supplychain "
           f"WHERE [{cd}] IS NOT NULL AND [{cp}] IS NOT NULL{fclause}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [float(r[0]) for r in rows], [float(r[1]) for r in rows]


def fetch_order_status_dist(filters=None):
    c = col("orderstatus")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{c}], COUNT(*) FROM supplychain "
           f"WHERE [{c}] IS NOT NULL{fclause} GROUP BY [{c}] ORDER BY 2 DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [r[1] for r in rows]


def fetch_dept_sales(filters=None):
    cd = col("departmentname")
    cs = col("sales")
    fclause, params = _fc(filters)
    sql = (f"SELECT [{cd}], SUM([{cs}]) FROM supplychain "
           f"WHERE 1=1{fclause} GROUP BY [{cd}] ORDER BY 2 DESC")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows], [float(r[1]) for r in rows]
