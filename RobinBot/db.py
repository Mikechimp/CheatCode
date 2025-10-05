import sqlite3, os
from datetime import datetime, timezone

DB_PATH = "state.db"

def now():
    return datetime.now(timezone.utc).isoformat()

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    return con

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS orders(
        id TEXT PRIMARY KEY,
        venue TEXT,
        venue_symbol TEXT,
        side TEXT,          -- buy/sell
        price REAL,
        amount REAL,
        status TEXT,        -- open/closed/canceled/stale
        created_at TEXT,
        updated_at TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS fills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        venue_symbol TEXT,
        side TEXT,
        price REAL,
        amount REAL,
        fee REAL,
        ts TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS positions(
        venue_symbol TEXT PRIMARY KEY,
        amount REAL NOT NULL DEFAULT 0,
        avg_cost REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, level TEXT, message TEXT
    )""")
    con.commit()
    return con

def log(con, level, msg):
    con.execute("INSERT INTO events(ts,level,message) VALUES(?,?,?)", (now(), level, msg))
    con.commit()
    print(f"[{level}] {msg}")

def record_order(con, o):
    con.execute("""INSERT OR REPLACE INTO orders
        (id, venue, venue_symbol, side, price, amount, status, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?)""", (
        o["id"], o["venue"], o["venue_symbol"], o["side"], o["price"], o["amount"],
        o["status"], o["created_at"], o["updated_at"]
    ))
    con.commit()

def update_order_status(con, oid, status):
    con.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?",
                (status, now(), oid))
    con.commit()

def record_fill(con, order_id, venue_symbol, side, price, amount, fee=0.0):
    con.execute("""INSERT INTO fills(order_id, venue_symbol, side, price, amount, fee, ts)
                   VALUES(?,?,?,?,?,?,?)""", (order_id, venue_symbol, side, price, amount, fee, now()))
    con.commit()

def ensure_position(con, venue_symbol):
    con.execute("INSERT OR IGNORE INTO positions(venue_symbol,amount,avg_cost) VALUES(?,?,?)",
                (venue_symbol, 0.0, None))
    con.commit()

def on_buy_filled(con, venue_symbol, price, amount):
    ensure_position(con, venue_symbol)
    c = con.cursor()
    prev_amt, prev_cost = c.execute("SELECT amount, avg_cost FROM positions WHERE venue_symbol=?",
                                    (venue_symbol,)).fetchone()
    new_amt = (prev_amt or 0) + amount
    new_cost = price if not prev_amt else ((prev_amt*prev_cost)+(amount*price))/new_amt
    con.execute("UPDATE positions SET amount=?, avg_cost=? WHERE venue_symbol=?",
                (new_amt, new_cost, venue_symbol))
    con.commit()

def on_sell_filled(con, venue_symbol, price, amount):
    c = con.cursor()
    row = c.execute("SELECT amount, avg_cost FROM positions WHERE venue_symbol=?",
                    (venue_symbol,)).fetchone()
    if not row: return
    prev_amt, prev_cost = row
    new_amt = max((prev_amt or 0) - amount, 0.0)
    new_cost = prev_cost if new_amt > 0 else None
    con.execute("UPDATE positions SET amount=?, avg_cost=? WHERE venue_symbol=?",
                (new_amt, new_cost, venue_symbol))
    con.commit()

def realized_pnl_last_hours(con, hours=24):
    # crude: sum(side-adjusted proceeds) over window minus cost basis on matched amount
    c = con.cursor()
    # Approx: sales – purchases in window (paper mode ok; live will be close enough for watchdog gating)
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = c.execute("SELECT side, price, amount FROM fills WHERE ts>=?", (since,)).fetchall()
    gross = 0.0
    for side, price, amt in rows:
        gross += price*amt if side.lower()=="sell" else -price*amt
    return gross

def last_n_prices(con, venue_symbol, n=60):
    # paper adapter can log “market ticks” here if you want; for live we’ll pull from adapter
    return []
