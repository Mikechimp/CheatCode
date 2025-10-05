def analyze(spread_pct, vol_pct, recent_pnl, cfg):
    recs = []
    wd = cfg["watchdog"]
    if not wd["enabled"]:
        return recs
    if spread_pct is not None and spread_pct > wd["max_spread_pct"]:
        recs.append(f"Market spread {spread_pct:.2f}% > {wd['max_spread_pct']}% → avoid thin book.")
    if vol_pct is not None and vol_pct > wd["vol_threshold_pct"]:
        recs.append(f"Volatility {vol_pct:.2f}% > {wd['vol_threshold_pct']}% → consider widening buy/sell.")
    if recent_pnl is not None and recent_pnl < 0 and abs(recent_pnl) >= (wd["pnl_drawdown_pct"]/100):
        recs.append(f"PnL drawdown > {wd['pnl_drawdown_pct']}% window → consider pausing this pair.")
    return recs
