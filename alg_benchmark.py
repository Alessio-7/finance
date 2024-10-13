import os
import typing

from matplotlib import pyplot as plt

import alg
from market import Market, Stock


class MarketBenchmark(Market):
	def __init__(self, test_stocks: list = []):
		super(MarketBenchmark, self).__init__()
		self.stocks_full_history: dict = {}

		stock_dir = "./scenarios/current"
		#stock_dir = "./scenarios/worst_scenario"
		#stock_dir = "./scenarios/worst_worst_scenario"
		#stock_dir = "./scenarios/all_time"

		if len(test_stocks) == 0:
			test_stocks = os.listdir(stock_dir)
		for file in os.listdir(stock_dir):
			if file in test_stocks:
				with open(f"{stock_dir}/{file}", "r") as f:
					past = [float(line.rstrip()) for line in f.readlines() if len(line.rstrip()) > 0]
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

	def start_bench_mark(self, alg_classes: list, start: int = 20, params: tuple = ()) -> None:
		self.startFrom(start)
		algs = []
		for c in alg_classes:
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
	alg_class = alg.AllInAllOut
	params = (4, 0.05, 0.05, -10)
	"""
	for test_stocks in [['uber', 'dis'], ['amzn', 'meta']]:
		m = MarketBenchmark(test_stocks=test_stocks)
		stats = m.stats_single_benchmark(alg_class=alg_class, params=params)
		print(test_stocks, ":", stats['tot capital'], stats['n transactions'])
	"""
	test_stocks = ['msft', 'nflx', 'nvda', 'aapl']
	m = MarketBenchmark(test_stocks=test_stocks)
	m.start_bench_mark(alg_classes=[alg_class], params=params)
	plt.show()
