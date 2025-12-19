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
        
    def _rsi(self, index, length=14):
        if index < length:
            return None

        gains = 0.0
        losses = 0.0

        for i in range(index - length + 1, index + 1):
            prev_close = self.data[i - 1]['close']
            close = self.data[i]['close']
            delta = close - prev_close

            if delta > 0:
                gains += delta
            else:
                losses -= delta

        if losses == 0:
            return 100.0

        rs = gains / losses
        return 100 - (100 / (1 + rs))
        
    def buy_condition(self, index) -> bool:
        """
        Buy when RSI(14) < 20 && time is between 9:30 and 16:00
        """
        if self.current_position is not None:
            return False
        
        # Check unix timestamp
        ts = self.data[index]['timestamp']
        dt = datetime.fromtimestamp(ts, tz=ZoneInfo("America/New_York"))

        if not (dt.hour > 9 or (dt.hour == 9 and dt.minute >= 30)):
            return False
        if not (dt.hour < 16):
            return False

        rsi = self._rsi(index)
        if rsi is None:
            return False

        if rsi < 20:
            self.current_position = self.data[index]['close']
            return True

        return False

    def sell_condition(self, index) -> bool:
        """
        Sell when RSI(14) > 80 && time is between 9:30 and 16:00
        """
        if self.current_position is None:
            return False
        
        # Check unix timestamp
        ts = self.data[index]['timestamp']
        dt = datetime.fromtimestamp(ts, tz=ZoneInfo("America/New_York"))

        if not (dt.hour > 9 or (dt.hour == 9 and dt.minute >= 30)):
            return False
        if not (dt.hour < 16):
            return False

        rsi = self._rsi(index)
        if rsi is None:
            return False

        if rsi > 80:
            self.current_position = None
            return True

        return False

    
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
