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
        pass
    
    def sell_condition(self, index) -> bool:
        pass
    
    def run(self):
        for i in range(len(self.data)):
            if self.buy_condition(i):
                self.trades.append(('buy', self.data[i]))
            elif self.sell_condition(i):
                self.trades.append(('sell', self.data[i]))
        return self.trades
    
    def evaluate(self, results):
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
            self.max_realized_drawdown = max(
                self.max_realized_drawdown,
                peak - equity
            )

        # -------- unrealized drawdown --------
        in_position = False
        entry_price = 0.0
        peak_price = 0.0
        self.max_unrealized_drawdown = 0.0

        trade_idx = 0

        for i in range(len(self.data)):
            price = self.data[i]

            if trade_idx < len(self.trades):
                action, trade_price = self.trades[trade_idx]

                if action == 'buy':
                    in_position = True
                    entry_price = trade_price
                    peak_price = trade_price
                    trade_idx += 1

                elif action == 'sell':
                    in_position = False
                    trade_idx += 1

            if in_position:
                peak_price = max(peak_price, price)
                dd = peak_price - price
                self.max_unrealized_drawdown = max(
                    self.max_unrealized_drawdown,
                    dd
                )

        return {
            'avg_profit': self.avg_profit,
            'avg_loss': self.avg_loss,
            'win_rate': self.win_rate,
            'max_realized_drawdown': self.max_realized_drawdown,
            'max_unrealized_drawdown': self.max_unrealized_drawdown,
            'total_return': self.total_return
        }
