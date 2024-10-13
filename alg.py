import datetime

import numpy as np
from matplotlib import pyplot as plt

from market import Market, Stock


class AlgorithmStrategy:
	def __init__(self, market: Market, alg_name: str = "base_alg", start_capital: float = 10000):
		self.name = alg_name
		self.market: Market = market
		self.portfolio: dict = {stock.name: 0 for stock in self.market.stocks}
		self.capital: float = start_capital
		self.start_capital = start_capital
		self.tick_count = 0
		self.capital_history: list = [[0], [start_capital], [start_capital]]
		self.log_disabled = False
		self.log_file = None
		self.n_tran = 0

	def buy_sell(self, stock: Stock) -> tuple:
		raise NotImplementedError()

	def tick(self) -> None:
		self.tick_count += 1
		capital_changed = False
		for stock in self.market.stocks:
			to_buy, to_sell = self.buy_sell(stock)
			if to_buy + to_sell > 0:
				self.n_tran += to_buy + to_sell
				capital_changed = True
				if to_buy > 0:
					self.portfolio[stock.name] += to_buy
					self.capital -= stock.price() * to_buy
					self.log(f"buyed {to_buy} {stock.name}")

				if self.portfolio[stock.name] < to_buy:
					raise Exception("not enough stocks in portfolio")

				if to_sell > 0:
					self.portfolio[stock.name] -= to_sell
					self.capital += stock.price() * to_sell
					self.log(f"selled {to_sell} {stock.name}")

				self.capital = round(self.capital, 2)

				self.log(f"\tportfolio: {self.portfolio}")
				self.log(f"\tcapital: {self.capital}")
		if capital_changed:
			self.capital_history[0].append(self.tick_count)
			self.capital_history[1].append(self.capital)
			self.capital_history[2].append(self.tot_capital())

	def open_log(self) -> None:
		self.log_file = open(f"./logs/{self.name}.log", "a+")

	def close_log(self) -> None:
		self.log_file.close()
		self.log_file = None

	def log(self, log: str) -> None:
		if self.log_disabled:
			return

		if self.log_file is None:
			self.open_log()

		t = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M:%S.%f") + f" tick{self.tick_count}\t"
		self.log_file.write(t + log + "\n")

	def clean_log(self) -> None:
		open(f"./logs/{self.name}.log", "w").close()

	def tot_capital(self) -> float:
		return round(self.capital + sum([self.market.stock_by_name(name).price() * n for name, n in self.portfolio.items()]), 2)

	def stats(self) -> dict:
		return {
			'name': self.name,
			'n transactions': self.n_tran,
			'revenue': self.capital,
			'max capital': max(self.capital_history[1]),
			'min capital': min(self.capital_history[1]),
			'final portfolio': self.portfolio,
			'tot capital': self.tot_capital()
		}

	def print_stats(self) -> None:
		stats = self.stats()
		stats.pop('name')
		print(f"""-----{self.name}-----""")
		for k, v in stats.items():
			print(f"{k}: {v}")

	def gen_fig(self, fig_index=0) -> None:
		t = np.arange(0, self.market.history_len())

		fig = plt.figure(fig_index)
		fig.suptitle(self.name)
		axs = fig.subplots(2)
		for s in self.market.stocks:
			axs[0].plot(t, s.past, label=s.name)
		axs[1].plot(self.capital_history[0], self.capital_history[1], 'o-', label="capital")
		axs[1].plot(self.capital_history[0], self.capital_history[2], 'o-', label="tot capital")
		axs[1].axhline(0, color='r', linewidth=0.5)

		axs[0].grid()
		axs[1].grid()
		axs[1].set_xlim(axs[0].get_xlim())
		fig.legend(loc="center right")
		fig.set_figwidth(13)


class Simple(AlgorithmStrategy):
	def __init__(self, market: Market, start_capital: float = 10000, params: tuple = (0.02, 0.01, -0.01, 0.05, 1)):
		super().__init__(market, alg_name="Simple", start_capital=start_capital)
		self.buyed_price: dict = {stock.name: [] for stock in self.market.stocks}

		if len(params) != 5:
			params = (0.02, 0.01, -0.01, 0.05, 1)

		self.profit_percent = params[0]
		self.percent_range_buy = params[1]
		self.min_trend_buy, self.max_trend_buy = params[2], params[3]
		self.n_buy = int(params[4])

	def in_error_range(self, confront: float, check: float, percent: float) -> bool:
		return confront * (-(1 + percent)) <= check <= confront * (1 + percent)

	def avg_stock_price(self, name: str) -> float:
		return (sum(self.buyed_price[name]) / len(self.buyed_price[name])) if len(self.buyed_price[name]) > 0 else 0

	def buy_sell(self, stock: Stock) -> tuple:
		buy = 0
		sell = 0

		if stock.price() >= self.avg_stock_price(stock.name) * (1 + self.profit_percent) and self.portfolio[stock.name] > 0:
			sell = self.portfolio[stock.name]
			self.buyed_price[stock.name].clear()
		elif self.in_error_range(stock.historical_min(from_time=-5), stock.price(), self.percent_range_buy) and \
				self.min_trend_buy < stock.trend(from_time=-3) < self.max_trend_buy:
			buy = self.n_buy
			self.buyed_price[stock.name].append(stock.price())

		return buy, sell


class AllInAllOut(AlgorithmStrategy):
	def __init__(self, market: Market, start_capital: float = 10000, params=()):
		super().__init__(market, "AllInAllOut", start_capital)

		if len(params) != 4:
			params = (1, 0.03, 0.1, -10)

		self.n_stock_mov = int(params[0])
		self.buy_perc = params[1]
		self.sell_perc = params[2]
		self.time_comp = int(params[3])

	def buy_sell(self, stock: Stock) -> tuple:
		if self.portfolio[stock.name] == 0 and stock.price() < stock.historical_average(from_time=self.time_comp) * (1 + self.buy_perc):
			return self.n_stock_mov, 0
		if self.portfolio[stock.name] > 0 and stock.price() > stock.historical_average(from_time=self.time_comp) * (1 + self.sell_perc):
			return 0, self.n_stock_mov
		return 0, 0
