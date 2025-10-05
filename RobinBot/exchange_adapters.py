import time, uuid, random
import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from dotenv import load_dotenv

class Order:
    def __init__(self, venue, venue_symbol, side, price, amount):
        self.id = str(uuid.uuid4())
        self.venue = venue
        self.venue_symbol = venue_symbol
        self.side = side
        self.price = float(price)
        self.amount = float(amount)
        self.status = "open"
        self.created_at = self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def as_dict(self):
        return {
            "id": self.id, "venue": self.venue, "venue_symbol": self.venue_symbol,
            "side": self.side, "price": self.price, "amount": self.amount,
            "status": self.status, "created_at": self.created_at, "updated_at": self.updated_at
        }

class PaperAdapter:
    """Very simple simulator: price follows a noisy walk; limit orders fill if crossed."""
    def __init__(self, seed_price_map):
        self.venue = "paper"
        self.prices = dict(seed_price_map)    # { "ETH-USD": 2000.0, ... }
        self.open_orders = {}                 # order_id -> Order

    def tick(self, venue_symbol):
        p = self.prices[venue_symbol]
        # random walk with ±0.2% step
        step = p * random.uniform(-0.002, 0.002)
        self.prices[venue_symbol] = max(0.0001, p + step)
        return self.prices[venue_symbol]

    def fetch_price(self, venue_symbol):
        return self.tick(venue_symbol)

    def place_limit_buy(self, venue_symbol, price, amount):
        o = Order(self.venue, venue_symbol, "buy", price, amount)
        self.open_orders[o.id] = o
        return o.as_dict()

    def place_limit_sell(self, venue_symbol, price, amount):
        o = Order(self.venue, venue_symbol, "sell", price, amount)
        self.open_orders[o.id] = o
        return o.as_dict()

    def fetch_open_orders(self, venue_symbol):
        return [o.as_dict() for o in self.open_orders.values() if o.venue_symbol==venue_symbol and o.status=="open"]

    def try_fill(self, venue_symbol):
        # Fill any crossed limits at exact limit price for simplicity
        px = self.prices[venue_symbol]
        filled = []
        for o in list(self.open_orders.values()):
            if o.venue_symbol != venue_symbol or o.status != "open": continue
            if o.side == "buy" and px <= o.price:
                o.status = "closed"; o.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); filled.append(o)
            if o.side == "sell" and px >= o.price:
                o.status = "closed"; o.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); filled.append(o)
        return [o.as_dict() for o in filled]

    # --- helper for bot loop ---
    def poll_and_fill(self, venue_symbol):
        self.fetch_price(venue_symbol)
        return self.try_fill(venue_symbol)

class RobinhoodAdapter:
    """
    Safe scaffold:
      - loads creds from .env
      - fetch_price(): implement using Robinhood Crypto quote endpoint
      - place_limit_buy/sell(): will NO-OP if dry_run is True
      - fetch_open_orders(), poll_and_fill(): reconcile order states
    Fill the TODOs using the official docs: https://docs.robinhood.com/  (Crypto Trading API)
    """
    def __init__(self, dry_run=True):
        load_dotenv()
        self.venue = "robinhood"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PingPongBot/1.0",
            # Add Authorization header once you obtain a bearer token or HMAC scheme from docs
            # "Authorization": f"Bearer {os.getenv('RH_ACCESS_TOKEN')}",
            # "X-API-KEY": os.getenv("RH_API_KEY"),
        })
        self.dry_run = dry_run
        # You will likely set a base URL from docs, e.g.:
        # self.base = "https://api.robinhood.com"            # Example only — confirm in docs
        # self.crypto_base = "https://nummus.robinhood.com"   # Example only — confirm in docs

    def _idempotency_key(self):
        return str(uuid.uuid4())

    @retry(wait=wait_exponential(min=0.5, max=8), stop=stop_after_attempt(5))
    def _get(self, url, **kw):
        r = self.session.get(url, timeout=10, **kw)
        r.raise_for_status()
        return r.json()

    @retry(wait=wait_exponential(min=0.5, max=8), stop=stop_after_attempt(5))
    def _post(self, url, json=None, **kw):
        r = self.session.post(url, json=json, timeout=10, **kw)
        r.raise_for_status()
        return r.json()

    # ---------- REQUIRED BY THE BOT ----------
    def fetch_price(self, venue_symbol: str) -> float:
        """
        TODO: Implement using Robinhood Crypto Quote endpoint.
        - Map venue_symbol like 'ETH-USD' to the symbol format the API expects.
        - Return a float price (last/mark/bid/ask per your preference).
        """
        raise NotImplementedError("Fill fetch_price() with the official quote endpoint.")

    def place_limit_buy(self, venue_symbol: str, price: float, amount: float, tif: str = "gtc"):
        """
        TODO: Implement with Robinhood limit BUY order endpoint.
        Respect self.dry_run: if True, do not POST; just return a fake order dict so the bot continues its loop.
        """
        if self.dry_run:
            # emulate an 'open' order object, bot tracks it until 'filled' via poll_and_fill()
            return {
                "id": self._idempotency_key(),
                "venue": self.venue,
                "venue_symbol": venue_symbol,
                "side": "buy",
                "price": float(price),
                "amount": float(amount),
                "status": "open",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        # LIVE: build payload from docs; include idempotency key if supported
        # payload = {...}
        # return self._post(f"{self.crypto_base}/orders", json=payload)
        raise NotImplementedError("Fill place_limit_buy() for live trading per docs.")

    def place_limit_sell(self, venue_symbol: str, price: float, amount: float, tif: str = "gtc"):
        if self.dry_run:
            return {
                "id": self._idempotency_key(),
                "venue": self.venue,
                "venue_symbol": venue_symbol,
                "side": "sell",
                "price": float(price),
                "amount": float(amount),
                "status": "open",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        # LIVE: build payload and POST to orders endpoint
        raise NotImplementedError("Fill place_limit_sell() for live trading per docs.")

    def fetch_open_orders(self, venue_symbol: str):
        """
        TODO: Implement using list-open-orders endpoint filtered by symbol.
        In dry_run, just return [] so the bot re-arms as needed, or track a local cache if you prefer.
        """
        return []

    def poll_and_fill(self, venue_symbol: str):
        """
        LIVE: Reconcile open->filled by querying order status.
        DRY_RUN: return [] to avoid generating fills (you’re doing quotes-only smoke testing).
        """
        return []

