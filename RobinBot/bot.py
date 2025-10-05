import os, time, yaml
from datetime import datetime, timezone
from db import init_db, log, record_order, update_order_status, record_fill, on_buy_filled, on_sell_filled, realized_pnl_last_hours
from exchange_adapters import PaperAdapter, RobinhoodAdapter
import watchdog

def send_signal(cfg, msg):
    s = cfg["reporting"].get("signal", {})
    if not s.get("enabled"): return
    try:
        import subprocess
        subprocess.run(["signal-cli","-u",s["sender_number"],"send",s["recipient_number"],"-m",msg], check=True)
    except Exception as e:
        print("[WARN] Signal send failed:", e)

def load_cfg():
    with open("config.yaml","r") as f: return yaml.safe_load(f)

def make_adapter(cfg):
    mode = cfg["mode"]
    if mode == "paper":
        # seed with buy_price or mid-range so sim crosses naturally
        seed = {st["venue_symbol"]: (st["buy_price"]+st["sell_price"])/2 for st in cfg["strategies"]}
        return PaperAdapter(seed)
    elif mode == "robinhood":
        # You’d pass keys via env vars once you wire the adapter.
        return RobinhoodAdapter(os.getenv("RH_KEY"), os.getenv("RH_SECRET"))
    else:
        raise ValueError("Unknown mode")

def main():
    cfg = load_cfg()
    con = init_db()
    ex = make_adapter(cfg)
    last_status_day = None

    while True:
        now = datetime.now()
        # Daily status
        dhour = cfg["reporting"].get("daily_status_hour_local")
        if dhour is not None and now.hour == int(dhour) and last_status_day != now.date():
            pnl24 = realized_pnl_last_hours(con, 24)
            send_signal(cfg, f"[STATUS] Bot alive. 24h realized PnL approx: {pnl24:.2f} {cfg['base_currency']}")
            last_status_day = now.date()

        for st in cfg["strategies"]:
            symbol = st["venue_symbol"]
            amt = float(st["amount"])
            buy_p = float(st["buy_price"])
            sell_p = float(st["sell_price"])
            good_til = st.get("good_til")

            # time window
            if good_til:
                end = datetime.fromisoformat(good_til)
                if datetime.now() > end:
                    continue

            # 1) Sync/Fill detection
            filled = ex.poll_and_fill(symbol)
            for o in filled:
                # Record fill + position accounting
                record_fill(con, o["id"], symbol, o["side"], o["price"], o["amount"], fee=0.0)
                if o["side"]=="buy": on_buy_filled(con, symbol, o["price"], o["amount"])
                else: on_sell_filled(con, symbol, o["price"], o["amount"])
                update_order_status(con, o["id"], "closed")
                log(con,"INFO",f"Filled {o['side']} {symbol} @ {o['price']} x {o['amount']}")

                # 2) Re-arm the ping-pong leg: if buy filled → place sell; if sell filled → place buy.
                try:
                    if o["side"]=="buy":
                        so = ex.place_limit_sell(symbol, sell_p, amt)
                        record_order(con, so); log(con,"INFO",f"Placed SELL {symbol} @ {sell_p}")
                    else:
                        bo = ex.place_limit_buy(symbol, buy_p, amt)
                        record_order(con, bo); log(con,"INFO",f"Placed BUY {symbol} @ {buy_p}")
                except Exception as e:
                    log(con,"ERROR",f"Re-arm failed for {symbol}: {e}")

            # 3) If neither leg is open, arm starting leg (BUY)
            opens = ex.fetch_open_orders(symbol)
            if not opens:
                try:
                    bo = ex.place_limit_buy(symbol, buy_p, amt)
                    record_order(con, bo); log(con,"INFO",f"Init BUY {symbol} @ {buy_p}")
                except Exception as e:
                    log(con,"ERROR",f"Init BUY failed {symbol}: {e}")

            # 4) Watchdog (very light)
            try:
                # For paper adapter we can approximate spread=0, vol from price wiggle if you want to extend
                recs = watchdog.analyze(spread_pct=None, vol_pct=None,
                                        recent_pnl=abs(realized_pnl_last_hours(con, cfg["watchdog"]["pnl_drawdown_window_hours"])) / max(1.0, st["sell_price"]*st["amount"]) * 100.0,
                                        cfg=cfg)
                if recs:
                    msg = f"[WATCHDOG] {symbol}: " + " | ".join(recs)
                    log(con,"WARN",msg)
                    send_signal(cfg, msg)
            except Exception as e:
                log(con,"WARN",f"Watchdog error: {e}")

        time.sleep(int(cfg["poll_seconds"]))

if __name__ == "__main__":
    main()
