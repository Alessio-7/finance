import os
import typing

from matplotlib import pyplot as plt

import alg
from market import Market, Stock


class BenchmarkStock(Stock):

	def __init__(self, name: str, end_index: int, past: list = None):
		super().__init__(name, past)
		self.end_index = end_index if end_index > 0 else len(self.past) + end_index

	def price(self) -> float:
		try:
			return self.past[self.end_index]
		except Exception:
			print(self.end_index, len(self.past))

	def historical_average(self, from_time: int = 0, to_time: int = -2) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")
		return super().historical_average(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def historical_min(self, from_time: int = 0, to_time: int = -2) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().historical_min(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def historical_max(self, from_time: int = 0, to_time: int = -2) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().historical_max(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def trend(self, from_time: int = -2, to_time: int = -2) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().trend(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def next(self):
		self.end_index += 1


class MarketBenchmark(Market):
	def __init__(self, scenario: str = None, stocks_scenario: list[str] = None):
		super(MarketBenchmark, self).__init__()
		if stocks_scenario is None:
			stocks_scenario = []

		self.n_benchmarks = 0
		self.loaded_scenario: str = ""
		if scenario is not None:
			self.load_scenario(scenario, stocks_scenario)

	def load_scenario(self, scenario: str = "current", stocks_scenario: list[str] = None):
		if self.loaded_scenario == scenario:
			return
		self.loaded_scenario = scenario
		if stocks_scenario is None:
			stocks_scenario = []

		stock_dir = f"./scenarios/{scenario}"
		if len(stocks_scenario) == 0:
			stocks_scenario = os.listdir(stock_dir)
		for file in os.listdir(stock_dir):
			if file in stocks_scenario:
				with open(f"{stock_dir}/{file}", "r") as f:
					past = [float(line.rstrip()) for line in f.readlines() if len(line.rstrip()) > 0]
				self.stocks.append(BenchmarkStock(file, past=past, end_index=-1))

	def startFrom(self, time: int) -> None:
		for stock in self.stocks:
			stock.end_index = time

	def next(self) -> None:
		for stock in self.stocks:
			stock.next()

	def history_len(self) -> int:
		return self.stocks[0].end_index + 1

	def time_left(self) -> int:
		return len(self.stocks[0].past) - self.history_len()

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
	m = MarketBenchmark(scenario="daily/2024-10-18")
	m.start_bench_mark(
		alg_class=alg.OneInAllOut,
		params=[1.0, -0.005, 0.01, -20.0]
	)
	plt.show()
