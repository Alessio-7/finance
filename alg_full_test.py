import typing

import numpy as np
from matplotlib import pyplot as plt

import alg
from alg_benchmark import MarketBenchmark
from alg_best_fitter import best_fitting_params


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
			benchmark.load_scenario(scenario=scenario)
			benchmark.start_bench_mark(alg_class=self.alg_class, params=params)


transaction_costs = np.linspace(0.01, 0.1, 3)

algs = [
	TestAlg(
		alg_class=alg.OneInAllOut,
		bounds=[(1, 1), (-0.1, 0.1), (-0.1, 0.1), (-15, -2)],
		iterations=[1, 20, 20, 13]
	)
]

scen = "daily/2024-10-18"

for scenario in [scen]:
	for a in algs:
		a.gen_best_params(scenario)
for a in algs:
	a.print_best_params()

algs[0].launch_benchmark()
plt.show()
