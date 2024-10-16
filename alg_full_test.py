import typing

import numpy as np

import alg
from alg_best_fitter import best_fitting_params


class TestAlg:
	def __init__(self, alg_class: typing.ClassVar, bounds: list[tuple[float, float]], iterations: list[int]):
		self.alg_class = alg_class
		self.bounds = bounds
		self.iterations = iterations

		self.best_params_scenario: dict[str: tuple[list, float]] = {}

	def gen_best_params(self, scenario: str):
		self.best_params_scenario[scenario] = best_fitting_params(self.alg_class, self.bounds, self.iterations, scenario=scenario)

	def print_best_params(self):
		with open(f"./logs/{self.alg_class.__name__}_params", "w+") as log_file :
			print(f"name:\t{self.alg_class.__name__}")
			for scenario, (params, result) in self.best_params_scenario.items():
				print(f"\t-{scenario}:\t{params} -> {result}")
				log_file.write(f"{scenario}: {params} -> {result}\n")


transaction_costs = np.linspace(0.01, 0.1, 3)

algs = [
	TestAlg(
		alg_class=alg.OneInAllOut,
		bounds=[(1, 1), (-0.5, 0), (0, 0.5), (-15, -2)],
		iterations=[1, 15, 15, 13]
	)
]

"""for cost in transaction_costs:
	alg.transaction_cost = lambda price: price * transaction_costs
	print(f"\n\n__________________ transaction: {cost * 100}% __________________")"""


for scenario in ["current", "worst_worst_scenario"]:
	for a in algs:
		a.gen_best_params(scenario)
for a in algs:
	a.print_best_params()
