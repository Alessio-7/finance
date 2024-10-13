import os
import typing

import matplotlib.pyplot as plt

import alg
from market import Market, Stock


class MarketBenchmark(Market):
    def __init__(self, test_stocks:list = []):
        super(MarketBenchmark, self).__init__()
        self.stocks_full_history: dict = {}

        stock_dir = "./clean"
        if len(test_stocks)==0:
            test_stocks = os.listdir(stock_dir)
        for file in os.listdir(stock_dir): 
            if file in test_stocks:
                with open(f"{stock_dir}/{file}", "r") as f:
                    past = [float(line.rstrip()) for line in f.readlines()]
                self.stocks_full_history[file] = past

    def startFrom(self, time: int = -1) -> None:
        self.stocks = [Stock(name, past[:time]) for name, past in self.stocks_full_history.items()]

    def next(self, time: int = 1) -> None:
        for stock in self.stocks:
            stock.past.extend(self.stocks_full_history[stock.name][len(stock.past):len(stock.past) + time])

    def time_left(self) -> int:
        return len(self.stocks_full_history[self.stocks[0].name]) - self.history_len()

    def cycle(self, tick_funcs: list) -> None:
        while self.time_left() > 0:
            for fun in tick_funcs:
                fun()
            self.next()

    def startBenchMark(self, algs_classes: list, start: int = 20, params: tuple = ()) -> None:
        self.startFrom(start)
        algs = []
        for c in algs_classes:
            algs.append(c(self, 0, params))
            algs[-1].tick_count = start
            algs[-1].clean_log()
        self.cycle([alg.tick for alg in algs])
        i = 0
        for a in algs:
            a.close_log()
            a.update_history()
            a.print_stats()
            a.gen_fig(fig_index=i)
            i += 1
        algs.clear()

    def stats_single_benchmark(self, alg_class: typing.ClassVar, params: tuple = (), start: int = 20) -> dict:
        self.startFrom(start)
        a: alg.AlgorithmStrategy = alg_class(self, 0, params=params)
        a.tick_count = start
        a.log_disabled = True
        self.cycle([a.tick]), 
        a.update_history()
        return a.stats()


if __name__ == '__main__':
    m = MarketBenchmark(test_stocks=['amzn', 'meta'])
    #m.startBenchMark(algs_classes=[alg.AllInAllOut], params=(4, 0.15789473684210525, 0.05263157894736842, -16))
    m.startBenchMark(algs_classes=[alg.AllInAllOut], params=(4, 0.1, 0.2, -10))
    plt.show()
