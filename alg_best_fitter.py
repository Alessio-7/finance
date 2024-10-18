import typing

import numpy as np

import alg
from alg_benchmark import MarketBenchmark

all_params: list
benchmark = MarketBenchmark()


def in_error(i, list, error):
	for p in list:
		if p * (1 - error) < i < p * (1 + error):
			return True
	return False


def recursive_params(bounds: list[tuple[float, float]], iterations: list[int], params: list, index: int = 0) -> list:
	if len(params) == len(bounds):
		return params
	else:
		for x in np.linspace(bounds[index][0], bounds[index][1], iterations[index]):
			p = recursive_params(bounds=bounds, iterations=iterations, index=index + 1, params=params + [x])
			if p is not None:
				all_params.append(p)


def best_fitting_params(alg_class: typing.ClassVar, bounds: list[tuple[float, float]], iterations: list[int], scenario: str, result_type: int = 0) -> tuple[
	list, float]:
	global all_params

	benchmark.load_scenario(scenario)

	best_result = None
	best_params = []
	all_params = list()
	recursive_params(bounds=bounds, iterations=iterations, params=[])

	combinations = len(all_params)

	print(f"checking {combinations} combinations: ", end="")
	i = 0
	for params in all_params:
		i += 1
		#if in_error(combinations / i, [0.25, 0.5, 0.75, 1], 0.01):
		#	print("-", end="")
		if combinations/2 == i or combinations/2 +1 == i:
			print("-", end="")
		stats = benchmark.stats_single_benchmark(alg_class, params)

		if result_type == 0:
			result = stats['tot capital']
		elif result_type == 1:
			result = stats['tot capital'] / (abs(stats['liquid']) + 1)
		else:
			result = stats['tot capital']

		if best_result is None:
			best_result = result
			best_params = params

		if result > best_result:
			best_result = result
			best_params = params
	print()

	return [round(float(a), 2) for a in best_params], best_result


if __name__ == '__main__':
	alg_class = alg.OneInAllOut

	params = (1, 0.03, 0.1, -10)
	bounds = [(1, 1), (-0.5, 0), (0, 0.5), (-15, -2)]
	iters = [1, 15, 15, 13]

	bp, br = best_fitting_params(alg_class, bounds=bounds, iterations=iters, scenario="daily/2024-10-18")

	print(f"{bp} : {br}")
