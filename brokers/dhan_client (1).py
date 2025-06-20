from brokers.super_order import SuperOrder
from brokers.order import Order
from brokers.portfolio import Portfolio
from brokers.funds import Funds
from brokers.option_chain import OptionChain
from brokers.historical_data import HistoricalData
from brokers.trader_control import TraderControl
from brokers.market_feed import MarketFeed
from brokers.order_update import OrderUpdate
from brokers.full_depth import FullDepth

class DhanClient:
    def __init__(self, context):
        self.super_order = SuperOrder(context)
        self.order = Order(context)
        self.portfolio = Portfolio(context)
        self.funds = Funds(context)
        self.option_chain = OptionChain(context)
        self.historical_data = HistoricalData(context)
        self.trader_control = TraderControl(context)
        self.market_feed = MarketFeed(context)
        self.order_update = OrderUpdate(context)
        self.full_depth = FullDepth(context)

    def describe_all(self):
        return {
            "super_order": self.super_order.describe(),
            "order": self.order.describe(),
            "portfolio": self.portfolio.describe(),
            "funds": self.funds.describe(),
            "option_chain": self.option_chain.describe(),
            "historical_data": self.historical_data.describe(),
            "trader_control": self.trader_control.describe(),
            "market_feed": self.market_feed.describe(),
            "order_update": self.order_update.describe(),
            "full_depth": self.full_depth.describe()
        }
