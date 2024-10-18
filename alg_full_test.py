import typing

import numpy as np
from matplotlib import pyplot as plt

import alg
from alg_benchmark import MarketBenchmark
from alg_best_fitter import best_fitting_params, best_fitting_daily_params


class TestAlg:
	def __init__(self, alg_class: typing.ClassVar, bounds: list[tuple[float, float]], iterations: list[int]):
		self.alg_class = alg_class
		self.bounds = bounds
		self.iterations = iterations

		self.best_params_scenario: dict[str: tuple[list, float]] = {}

	def gen_best_params(self, scenario: str):
		self.best_params_scenario[scenario] = best_fitting_params(
			alg_class=self.alg_class,
			bounds=self.bounds,
			iterations=self.iterations,
			scenario=scenario
		)

	def gen_best_daily_params(self, day: str):
		self.best_params_scenario[f"daily/{day.removeprefix('daily/')}"] = best_fitting_daily_params(
			alg_class=self.alg_class,
			bounds=self.bounds,
			iterations=self.iterations,
			day=day
		)

	def print_best_params(self):
		with open(f"./logs/{self.alg_class.__name__}_params", "w+") as log_file:
			print(f"name:\t{self.alg_class.__name__}")
			for scenario, (params, result) in self.best_params_scenario.items():
				print(f"\t-{scenario}:\t{params} -> {result}")
				log_file.write(f"{scenario}: {params} -> {result}\n")

	def launch_benchmark(self):
		print("\n")
		benchmark = MarketBenchmark()
		for scenario, (params, result) in self.best_params_scenario.items():
			if scenario.startswith("daily/"):
				benchmark.daily_norm_reproduce(alg_class=self.alg_class, params=params, show=True)
			else:
				benchmark.load_scenario(scenario=scenario)
				benchmark.start_bench_mark(alg_class=self.alg_class, params=params)


transaction_costs = np.linspace(0.01, 0.1, 3)

algs = [
	TestAlg(
		alg_class=alg.OneInAllOut,
		bounds=[(1, 1), (-0.5, 0), (0, 0.1), (-10, -2)],
		iterations=[1, 5, 10, 8]
	)
]

scen = "2024-10-18"

for scenario in [scen]:
	for a in algs:
		a.gen_best_daily_params(scenario)
for a in algs:
	a.print_best_params()

algs[0].launch_benchmark()
plt.show()
