import time, uuid, random

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
    """Skeleton. You wire these to the Robinhood Crypto API.
    Keep method names compatible with PaperAdapter so the bot code doesn't change."""
    def __init__(self, api_key=None, api_secret=None):
        self.venue = "robinhood"
        # TODO: auth/session bootstrap

    def fetch_price(self, venue_symbol):
        # TODO: GET quote for venue_symbol
        raise NotImplementedError

    def place_limit_buy(self, venue_symbol, price, amount, tif="gtc"):
        # TODO: POST limit buy
        raise NotImplementedError

    def place_limit_sell(self, venue_symbol, price, amount, tif="gtc"):
        # TODO: POST limit sell
        raise NotImplementedError

    def fetch_open_orders(self, venue_symbol):
        # TODO: GET open orders
        raise NotImplementedError

    def poll_and_fill(self, venue_symbol):
        """For live: just return any newly closed orders by reconciling open->closed via API."""
        # Implement by fetching order statuses and returning any transitions to 'filled'
        raise NotImplementedError
