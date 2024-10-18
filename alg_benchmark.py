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

	def historical_average(self, from_time: int = 0, to_time: int = -1) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")
		return super().historical_average(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def historical_min(self, from_time: int = 0, to_time: int = -1) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().historical_min(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def historical_max(self, from_time: int = 0, to_time: int = -1) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().historical_max(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def trend(self, from_time: int = -2, to_time: int = -1) -> float:
		if from_time > self.end_index or to_time > self.end_index:
			raise IndexError(f"from_time and to_time has to be < {self.end_index}")

		return super().trend(
			from_time=from_time if from_time > 0 else self.end_index + from_time + 1,
			to_time=to_time if to_time > 0 else self.end_index + to_time + 1
		)

	def next(self):
		self.end_index += 1


class ReproduceMoves(alg.AlgorithmStrategy):
	def __init__(self, market: Market, start_capital: float, moves: dict[int: tuple[int, int]]):
		super().__init__(market, "Reproducing", start_capital)
		self.moves: dict[int: tuple[int, int]] = moves

	def buy_sell(self, stock: Stock) -> tuple[int, int]:
		if self.tick_count in self.moves[stock.name]:
			return self.moves[stock.name][self.tick_count]
		return 0, 0


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
		self.stocks.clear()
		if len(stocks_scenario) == 0:
			stocks_scenario = os.listdir(stock_dir)
		for file in os.listdir(stock_dir):
			if file in stocks_scenario:
				with open(f"{stock_dir}/{file}", "r") as f:
					past = [float(line.rstrip()) for line in f.readlines() if len(line.rstrip()) > 0]
				self.stocks.append(BenchmarkStock(file, past=past, end_index=-1))

	def start_from(self, time: int) -> None:
		if self.loaded_scenario=="" or self.loaded_scenario is None:
			raise Exception("scenario not loaded")

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

	def start_bench_mark(self, alg_class: typing.ClassVar, start: int = 20, params: list = None) -> tuple[plt.Figure, dict]:
		if params is None:
			params = []

		self.start_from(start)
		a = alg_class(self, 0, params)
		a.tick_count = start
		a.clear_log()

		self.cycle(a.tick)

		a.close_log()
		a.update_history()
		a.print_stats()
		self.n_benchmarks += 1
		return a.gen_fig(fig_index=self.n_benchmarks), a.stats()

	def stats_single_benchmark(self, alg_class: typing.ClassVar, params: list = None, start: int = 20) -> dict[str, typing.Any]:
		if params is None:
			params = []

		self.start_from(start)
		a: alg.AlgorithmStrategy = alg_class(self, 0, params=params)
		a.tick_count = start
		a.disable_log()
		self.cycle(a.tick)
		a.update_history()
		return a.stats()

	def reproduce_moves(self, moves: dict[str: dict[int: tuple[int, int]]], scenario: str, start: int = 20, show: bool = False):
		self.load_scenario(scenario)
		self.start_from(start)

		reproduce = ReproduceMoves(self, 0, moves)
		reproduce.tick_count = start
		reproduce.clear_log()
		# repr.disable_log()
		self.cycle(reproduce.tick)
		if show:
			reproduce.print_stats()
			self.n_benchmarks += 1
			return reproduce.gen_fig(fig_index=self.n_benchmarks)
		else:
			return reproduce.stats()

	def daily_norm_reproduce(self, alg_class: typing.ClassVar, params: list = None, day: str = "2024-10-18", start: int = 20, show: bool = False):
		if params is None:
			params = []

		self.load_scenario(f"daily/{day.removeprefix('daily/')}_norm")
		self.start_from(start)
		stats: dict
		if show:
			_, s = self.start_bench_mark(
				alg_class=alg_class,
				params=params
			)
		else:
			s = self.stats_single_benchmark(
				alg_class=alg.OneInAllOut,
				params=params
			)

		# print(s['tot capital'])
		return self.reproduce_moves(moves=s['moves'], scenario=f"daily/{day.removeprefix('daily/')}", show=show)


if __name__ == '__main__':
	m = MarketBenchmark()

	m.daily_norm_reproduce(
		alg_class=alg.OneInAllOut,
		params=[1.0, -0.5, 0.0, -5],
		day="2024-10-18",
		show=True
	)
	plt.show()
