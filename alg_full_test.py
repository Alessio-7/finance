import typing

from matplotlib import pyplot as plt

import alg
from alg_benchmark import MarketBenchmark
from alg_best_fitter import best_fitting_params, best_fitting_daily_params


class TestAlg:
	def __init__(self, alg_class: typing.ClassVar, bounds: list[tuple[float, float]], iterations: list[int], threading_scale: int = 4):
		self.alg_class = alg_class
		self.bounds = bounds
		self.iterations = iterations
		self.threading_scale = threading_scale

		self.best_params_scenario: dict[str: tuple[list, float]] = {}

	def gen_best_params(self, scenario: str, stocks_scenario: list[str] = None):
		self.best_params_scenario[scenario] = best_fitting_params(
			alg_class=self.alg_class,
			bounds=self.bounds,
			iterations=self.iterations,
			scenario=scenario,
			stocks_scenario=stocks_scenario,
			threading_scale=self.threading_scale
			)

	def gen_best_daily_params(self, day: str, stocks_scenario: list[str] = None):
		self.best_params_scenario[f"daily/{day.removeprefix('daily/')}"] = best_fitting_daily_params(
			alg_class=self.alg_class,
			bounds=self.bounds,
			iterations=self.iterations,
			day=day,
			stocks_scenario=stocks_scenario,
			threading_scale=self.threading_scale
			)

	def print_best_params(self):
		with open(f"./logs/{self.alg_class.__name__}_params", "w+") as log_file:
			print(f"name:\t{self.alg_class.__name__}")
			for scenario, (params, result) in self.best_params_scenario.items():
				print(f"\t-{scenario}:\t{params} -> {result}")
				log_file.write(f"{scenario}: {params} -> {result}\n")

	def launch_benchmark(self, stocks_scenario: list[str] = None):
		print("\n")
		benchmark = MarketBenchmark()
		for scenario, (params, result) in self.best_params_scenario.items():
			if scenario.startswith("daily/"):
				benchmark.daily_norm_reproduce(
					alg_class=self.alg_class,
					day=scenario,
					stocks_scenario=stocks_scenario,
					params=params,
					print_stats=True,
					show=True
					)
			else:
				benchmark.start_benchmark(
					alg_class=self.alg_class,
					scenario=scenario,
					stocks_scenario=stocks_scenario,
					params=params,
					print_stats=True
					)


if __name__ == '__main__':
	algs = [
		TestAlg(
			alg_class=alg.OneInAllOut,
			bounds=[(1, 1), (-5, 5), (-5, 5), (-15, -2)],
			iterations=[1, 100, 100, 13],
			# iterations=[1, 5, 4, 4],
			threading_scale=10
			)
		]

	scen = "2024-10-18"
	stcks = ['msft']
	for s in [scen]:
		for a in algs:
			a.gen_best_daily_params(day=s, stocks_scenario=stcks)
	for a in algs:
		a.print_best_params()

	algs[0].launch_benchmark(stocks_scenario=stcks)
	plt.show()
