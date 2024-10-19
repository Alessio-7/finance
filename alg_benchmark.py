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
		return self.past[self.end_index]

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
	def __init__(self):
		super(MarketBenchmark, self).__init__()

		self.n_benchmarks = 0
		self.loaded_scenario: str = ""

	def load_scenario(self, scenario: str = "current", stocks_scenario: list[str] = None, start: int = -1):
		if scenario is None or scenario == "":
			scenario = "current"
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
				self.stocks.append(BenchmarkStock(file, past=past, end_index=start))

	def start_from(self, start: int):
		if self.loaded_scenario == "" or self.loaded_scenario is None:
			raise Exception("scenario not loaded")

		for stock in self.stocks:
			stock.end_index = start

	def next(self):
		for stock in self.stocks:
			stock.next()

	def history_len(self) -> int:
		return self.stocks[0].end_index + 1

	def time_left(self) -> int:
		return len(self.stocks[0].past) - self.history_len()

	def cycle(self, tick_fun: typing.Callable):
		while self.time_left() > 0:
			tick_fun()
			self.next()

	def start_benchmark(
			self,
			alg_class: typing.ClassVar,
			scenario: str = None,
			stocks_scenario: list[str] = None,
			params: list = None,
			start: int = 20,
			print_stats: bool = True
			) -> tuple[plt.Figure, dict[str, typing.Any]]:

		if params is None:
			params = []

		self.load_scenario(scenario=scenario, stocks_scenario=stocks_scenario, start=start)
		a = alg_class(self, start_capital=0, params=params)
		a.tick_count = start
		a.clear_log()

		self.cycle(a.tick)

		a.close_log()
		a.update_history()

		if print_stats:
			a.print_stats()
		self.n_benchmarks += 1
		return a.gen_fig(fig_index=self.n_benchmarks), a.stats()

	def stats_of_benchmark(
			self,
			alg_class: typing.ClassVar,
			scenario: str = None,
			stocks_scenario: list[str] = None,
			params: list = None,
			start: int = 20,
			print_stats: bool = False
			) -> dict[str, typing.Any]:

		if params is None:
			params = []

		self.load_scenario(scenario=scenario, stocks_scenario=stocks_scenario, start=start)
		a: alg.AlgorithmStrategy = alg_class(self, start_capital=0, params=params)
		a.tick_count = start
		a.disable_log()

		self.cycle(a.tick)

		a.update_history()
		if print_stats:
			a.print_stats()
		return a.stats()

	def reproduce_moves(
			self,
			moves: dict[str: dict[int: tuple[int, int]]],
			scenario: str,
			stocks_scenario: list[str],
			start: int,
			print_stats: bool = True,
			show: bool = False
			) -> tuple[plt.Figure, dict[str, typing.Any]]:

		self.load_scenario(scenario=scenario, stocks_scenario=stocks_scenario, start=start)
		reproduce = ReproduceMoves(self, start_capital=0, moves=moves)
		reproduce.tick_count = start
		reproduce.clear_log()
		# repr.disable_log()
		self.cycle(reproduce.tick)

		if print_stats:
			reproduce.print_stats()

		fig = None

		if show:
			self.n_benchmarks += 1
			fig = reproduce.gen_fig(fig_index=self.n_benchmarks)

		return fig, reproduce.stats()

	def daily_norm_reproduce(
			self,
			alg_class: typing.ClassVar,
			day: str = None,
			stocks_scenario: list[str] = None,
			params: list = None,
			start: int = 20,
			print_stats: bool = False,
			show: bool = False
			) -> tuple[plt.Figure, dict[str, typing.Any]]:

		if params is None:
			params = []

		scenario = f"daily/{day.removeprefix('daily/')}_norm"
		s: dict
		if show:
			_, s = self.start_benchmark(
				alg_class=alg_class,
				scenario=scenario,
				stocks_scenario=stocks_scenario,
				params=params,
				start=start,
				print_stats=print_stats
				)
		else:
			s = self.stats_of_benchmark(
				alg_class=alg.OneInAllOut,
				scenario=scenario,
				stocks_scenario=stocks_scenario,
				params=params,
				start=start,
				print_stats=print_stats
				)

		return self.reproduce_moves(
			moves=s['moves'],
			scenario=f"daily/{day.removeprefix('daily/')}",
			stocks_scenario=stocks_scenario,
			start=start,
			print_stats=print_stats,
			show=show
			)


if __name__ == '__main__':
	m = MarketBenchmark()
	m.daily_norm_reproduce(
		alg_class=alg.OneInAllOut,
		params=[1.0, -4.797979797979798, -1.7676767676767677, -4.166666666666668],
		#params=[1.0, -3.080808080808081, -2.676767676767677, -4.0],
		day="2024-10-18",
		stocks_scenario=["msft"],
		show=True,
		print_stats=True
		)
	plt.show()
