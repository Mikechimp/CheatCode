# 🪙 Ping-Pong Crypto Bot — Complete README

This project is a fully automated crypto trading bot that executes a simple, repeatable **“ping-pong” strategy**:

- **Buy** when price ≤ your set `buy_price`
- **Sell** when price ≥ your set `sell_price`
- **Repeat** indefinitely (or until `good_til` expires)
- **Track profit/loss** locally in an SQLite database
- **Optionally alert you** via Signal
- **Paper-mode safe:** simulate trades before going live
- **Robinhood-ready:** plug in Robinhood’s Crypto API later

---

## 🚀 Quick Start

### 1️⃣ Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
