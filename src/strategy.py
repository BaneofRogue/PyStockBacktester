from datetime import datetime
from zoneinfo import ZoneInfo


class Strategy:
    
    def __init__(self, data):
        self.data = data
        self.trades = []
        self.current_position = None
        
        # Metrics
        self.avg_profit = 0.0
        self.avg_loss = 0.0
        self.win_rate = 0.0
        self.max_realized_drawdown = 0.0
        self.max_unrealized_drawdown = 0.0
        self.total_return = 0.0
        self.results = []
        
    def buy_condition(self, index) -> bool:
        raise NotImplementedError("Buy condition not implemented.")
    
    def sell_condition(self, index) -> bool:
        raise NotImplementedError("Sell condition not implemented.")
    
    def run(self):
        for i in range(len(self.data)):
            if self.buy_condition(i):
                self.trades.append(('buy', self.data[i]))
            elif self.sell_condition(i):
                self.trades.append(('sell', self.data[i]))
        return self.trades
    
    def build_results(self):
        results = []
        entry = None

        for action, candle in self.trades:
            price = candle['close']

            if action == 'buy':
                entry = price

            elif action == 'sell' and entry is not None:
                profit = price - entry
                results.append({
                    'entry': entry,
                    'exit': price,
                    'profit': profit
                })
                entry = None

        return results
    
    def evaluate(self):
        results = self.build_results()

        profits = [r['profit'] for r in results if r['profit'] > 0]
        losses = [r['profit'] for r in results if r['profit'] <= 0]

        self.avg_profit = sum(profits) / len(profits) if profits else 0.0
        self.avg_loss = sum(losses) / len(losses) if losses else 0.0
        self.win_rate = len(profits) / len(results) if results else 0.0
        self.total_return = sum(r['profit'] for r in results)

        # -------- realized drawdown --------
        equity = 0.0
        peak = 0.0
        self.max_realized_drawdown = 0.0

        for r in results:
            equity += r['profit']
            peak = max(peak, equity)
            self.max_realized_drawdown = max(peak - equity, self.max_realized_drawdown)

        # -------- unrealized drawdown --------
        in_position = False
        peak_price = 0.0
        self.max_unrealized_drawdown = 0.0

        trade_idx = 0

        for i in range(len(self.data)):
            price = self.data[i]['close']

            if trade_idx < len(self.trades):
                action, candle = self.trades[trade_idx]
                trade_price = candle['close']

                if action == 'buy':
                    in_position = True
                    peak_price = trade_price
                    trade_idx += 1

                elif action == 'sell':
                    in_position = False
                    trade_idx += 1

            if in_position:
                peak_price = max(peak_price, price)
                self.max_unrealized_drawdown = max(
                    self.max_unrealized_drawdown,
                    peak_price - price
                )

        return {
            'avg_profit': self.avg_profit,
            'avg_loss': self.avg_loss,
            'win_rate': self.win_rate,
            'max_realized_drawdown': self.max_realized_drawdown,
            'max_unrealized_drawdown': self.max_unrealized_drawdown,
            'total_return': self.total_return
        }
