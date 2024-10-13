import numpy as np

from alg import AlgorithmStrategy, AllInAllOut
from alg_benchmark import MarketBenchmark

benchmark: MarketBenchmark
alg_class: AlgorithmStrategy.__class__


def alg(params: tuple) -> float:
	return benchmark.stats_single_benchmark(alg_class, params)['tot capital']


if __name__ == '__main__':
	benchmark = MarketBenchmark()
	alg_class = AllInAllOut

	params = (1, 0.03, 0.1, -10)
	bounds = [(1, 5), (0, 1.0), (0, 1.0), (-10, -2)]

	# max_val = minimize(lambda x: -alg(x), params, bounds=bounds)
	# print(max_val)

	iterations = 10
	fits = []

	best_result = 0
	best_params = ()

	for n_stock in range(bounds[0][0], bounds[0][1]+1):
		for buy_perc in np.linspace(bounds[1][0], bounds[1][1], iterations):
			for sell_perc in np.linspace(bounds[2][0], bounds[2][1], iterations):
				for time_comp in range(bounds[3][0], bounds[3][1]+1):
					params = (n_stock, buy_perc, sell_perc, time_comp)
					result = alg(params)
					if result > best_result:
						best_result = result
						best_params = params

	print(f"{best_params} : {best_result}")
