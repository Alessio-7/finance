import os
import typing

from matplotlib import pyplot as plt

import alg
from market import Market, Stock


class MarketBenchmark(Market):
	def __init__(self, scenario: str = "current", stocks_scenario: list[str] = None):
		super(MarketBenchmark, self).__init__()
		if stocks_scenario is None:
			stocks_scenario = []

		self.stocks_full_history: dict = {}
		self.n_benchmarks = 0
		self.loaded_scenario: str = ""
		self.load_scenario(scenario, stocks_scenario)

	def load_scenario(self, scenario: str = "current", stocks_scenario: list[str] = None):
		if self.loaded_scenario == scenario:
			return

		if stocks_scenario is None:
			stocks_scenario = []

		stock_dir = f"./scenarios/{scenario}"
		if len(stocks_scenario) == 0:
			stocks_scenario = os.listdir(stock_dir)
		for file in os.listdir(stock_dir):
			if file in stocks_scenario:
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

	def cycle(self, tick_fun: typing.Callable) -> None:
		while self.time_left() > 0:
			tick_fun()
			self.next()

	def start_bench_mark(self, alg_class: typing.ClassVar, start: int = 20, params: list = None) -> plt.Figure:
		if params is None:
			params = []

		self.startFrom(start)
		a = alg_class(self, 0, params)
		a.tick_count = start
		a.clean_log()

		self.cycle(a.tick)

		a.close_log()
		a.update_history()
		a.print_stats()
		self.n_benchmarks += 1
		return a.gen_fig(fig_index=self.n_benchmarks)

	def stats_single_benchmark(self, alg_class: typing.ClassVar, params: list = None, start: int = 20) -> dict[str, typing.Any]:
		if params is None:
			params = []

		self.startFrom(start)
		a: alg.AlgorithmStrategy = alg_class(self, 0, params=params)
		a.tick_count = start
		a.disable_log()
		self.cycle(a.tick)
		a.update_history()
		return a.stats()


if __name__ == '__main__':
	# TODO numero di azioni comprate in base alla liquidità FOURIER ANALISI
	m = MarketBenchmark(scenario="current")
	m.start_bench_mark(
		alg_class=alg.OneInAllOut,
		params=[1, 0.0, 0.5, -2.0]
	)
	plt.show()
