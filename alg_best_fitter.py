import multiprocessing as mp
import typing

import numpy as np

from alg_benchmark import MarketBenchmark


all_params: list


def recursive_params(bounds: list[tuple[float, float]], iterations: list[int], params: list, index: int = 0) -> list:
	"""deprecated"""
	if len(params) == len(bounds):
		return params
	else:
		for x in np.linspace(bounds[index][0], bounds[index][1], iterations[index]):
			p = recursive_params(bounds=bounds, iterations=iterations, index=index + 1, params=params + [float(x)])
			if p is not None:
				all_params.append(p)


def threading_combinations(
		threads_results: list,
		i: int,
		params_list: list,
		fun: typing.Callable,
		alg_class,
		scenario,
		stocks_scenario,
		result_type
		):
	"""deprecated"""
	print(f"\t{i}: {len(params_list)} combs")
	benchmark = MarketBenchmark()
	best_result = None
	best_params = []

	for params in params_list:
		stats = fun(
			self=benchmark,
			alg_class=alg_class,
			scenario=scenario,
			stocks_scenario=stocks_scenario,
			params=params,
			print_stats=False
			)

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
	print("-", end="")
	threads_results.append((best_params, best_result))


def best_fitting_params_fun(
		fun: typing.Callable,
		alg_class: typing.ClassVar,
		bounds: list[tuple[float, float]],
		iterations: list[int],
		scenario: str,
		stocks_scenario: list[str] = None,
		result_type: int = 0,
		threading_scale: int = 4
		) -> tuple[list[float], float]:
	"""deprecated"""
	global all_params

	all_params = list()
	recursive_params(bounds=bounds, iterations=iterations, params=[])

	combinations = len(all_params)

	print(f"checking {combinations} combinations: ")

	threads = []
	manager = mp.Manager()
	threads_results = manager.list()
	end_i = 0
	step = int(combinations / threading_scale)
	for i in range(threading_scale):
		start_i = end_i
		end_i += step
		params_list = all_params[start_i:end_i]
		threads.append(
			mp.Process(
				target=threading_combinations,
				args=(threads_results, i, params_list, fun, alg_class, scenario, stocks_scenario, result_type)
				)
			)

	if end_i < combinations - 1:
		threads.append(
			mp.Process(
				target=threading_combinations,
				args=(threads_results, threading_scale, all_params[end_i:], fun, alg_class, scenario, stocks_scenario, result_type)
				)
			)

	for t in threads:
		t.start()

	for t in threads:
		t.join()
	print()
	# print(threads_results)
	br = threads_results[0][1]
	bp: list = threads_results[0][0]

	for (par, res) in threads_results:
		if res > br:
			br = res
			bp = par

	print(bp, br)
	exit()
	return [round(float(a), 2) for a in bp], br


def best_fitting_params(
		alg_class: typing.ClassVar,
		bounds: list[tuple[float, float]],
		iterations: list[int],
		scenario: str,
		stocks_scenario: list[str] = None,
		result_type: int = 0,
		threading_scale: int = 4
		) -> tuple[list[float], float]:
	return best_fitting_params_fun(
		fun=MarketBenchmark.stats_of_benchmark,
		alg_class=alg_class,
		bounds=bounds,
		iterations=iterations,
		scenario=scenario,
		stocks_scenario=stocks_scenario,
		result_type=result_type,
		threading_scale=threading_scale
		)


def stats_output_daily_reproduce(**args):
	"""deprecated"""
	day = args.pop("scenario")
	args['day'] = day
	_, stats = MarketBenchmark.daily_norm_reproduce(**args)
	return stats


def best_fitting_daily_params(
		alg_class: typing.ClassVar,
		bounds: list[tuple[float, float]],
		iterations: list[int],
		day: str,
		stocks_scenario: list[str] = None,
		result_type: int = 0,
		threading_scale: int = 4
		) -> tuple[list[float], float]:
	print()

	return best_fitting_params_fun(
		fun=stats_output_daily_reproduce,
		alg_class=alg_class,
		bounds=bounds,
		iterations=iterations,
		scenario=day,
		stocks_scenario=stocks_scenario,
		result_type=result_type,
		threading_scale=threading_scale
		)
