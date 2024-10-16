import datetime
import typing

import numpy as np
from matplotlib import pyplot as plt

from market import Market, Stock

# transaction_cost = lambda price: price*0.1
transaction_cost = lambda price: 1


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

		if not self.log_disabled:
			self.open_log()

	def disable_log(self) -> None:
		if not self.log_disabled:
			self.log_disabled = True
			self.close_log()

	def buy_sell(self, stock: Stock) -> tuple[int, int]:
		raise NotImplementedError()

	def tick(self) -> None:
		capital_changed = False
		self.tick_count += 1
		for stock in self.market.stocks:
			to_buy, to_sell = self.buy_sell(stock)
			if to_buy + to_sell > 0:
				self.n_tran += to_buy + to_sell
				capital_changed = True
				if to_buy > 0:
					self.portfolio[stock.name] += to_buy
					self.capital -= (stock.price() * to_buy) + transaction_cost(stock.price())
					self.log(f"buy {to_buy} {stock.name}")

				if self.portfolio[stock.name] < to_buy:
					raise Exception("not enough stocks in portfolio")

				if to_sell > 0:
					self.portfolio[stock.name] -= to_sell
					self.capital += (stock.price() * to_sell) - transaction_cost(stock.price())
					self.log(f"sell {to_sell} {stock.name}")

				self.capital = round(self.capital, 2)

				self.log(f"\tportfolio: {self.portfolio}")
				self.log(f"\tcapital: {self.capital}")
		if capital_changed:
			self.update_history()

	def update_history(self) -> None:
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

		t = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M:%S.%f") + f" tick{self.tick_count}\t"
		self.log_file.write(t + log + "\n")

	def clean_log(self) -> None:
		open(f"./logs/{self.name}.log", "w").close()

	def tot_stock_value(self) -> float:
		return round(sum([self.market.stock_by_name(name).price() * n for name, n in self.portfolio.items()]), 2)

	def tot_capital(self) -> float:
		return round(self.capital + self.tot_stock_value(), 2)

	def stats(self) -> dict[str: typing.Any]:
		return {
			'name': self.name,
			'n transactions': self.n_tran,
			'max capital': max(self.capital_history[1]),
			'min capital': min(self.capital_history[1]),
			'final portfolio': self.portfolio,
			'liquid': self.capital,
			'tot stock value': self.tot_stock_value(),
			'tot capital': self.tot_capital(),
			# 'profit %': round((self.tot_capital() / (-self.capital if self.capital < 0 else 1)), 2)
			# 'profit %': round(tot_spent / tot_earned, 2)
		}

	def print_stats(self) -> None:
		stats = self.stats()
		stats.pop('name')
		print(f"""-----{self.name}-----""")
		for k, v in stats.items():
			print(f"{k}: {v}")

	def gen_fig(self, fig_index=0) -> plt.Figure:
		t = np.arange(0, self.market.history_len())

		fig = plt.figure(fig_index)
		fig.suptitle(self.name)
		axs = fig.subplots(2)
		for s in self.market.stocks:
			# print(len(s.past), s.name)
			axs[0].plot(t, s.past, label=s.name)
		axs[1].plot(self.capital_history[0], self.capital_history[1], 'o-', label="capital")
		axs[1].plot(self.capital_history[0], self.capital_history[2], 'o-', label="tot capital")
		axs[1].axhline(0, color='r', linewidth=0.5)

		axs[0].grid()
		axs[1].grid()
		axs[1].set_xlim(axs[0].get_xlim())
		fig.legend(loc="center right")
		fig.set_size_inches(13.5, 8.5)
		return fig


class AllInAllOut(AlgorithmStrategy):
	def __init__(self, market: Market, start_capital: float = 10000, params: list = None):
		super().__init__(market, "AllInAllOut", start_capital)

		if len(params) != 4 or params is None:
			params = (4, -0.1, 0.2, -10)

		self.n_stock_mov = int(params[0])
		self.buy_perc = params[1]
		self.sell_perc = params[2]
		self.time_comp = int(params[3])

	def buy_sell(self, stock: Stock) -> tuple[int, int]:
		if self.portfolio[stock.name] == 0 and stock.price() + (transaction_cost(stock.price()) / self.n_stock_mov) < stock.historical_average(
				from_time=self.time_comp) * (
				1 + self.buy_perc):
			return self.n_stock_mov, 0
		if self.portfolio[stock.name] > 0 and stock.price() - (transaction_cost(stock.price()) / self.n_stock_mov) > stock.historical_average(
				from_time=self.time_comp) * (
				1 + self.sell_perc):
			return 0, self.portfolio[stock.name]
		return 0, 0


class OneInAllOut(AlgorithmStrategy):
	def __init__(self, market: Market, start_capital: float = 10000, params: list = None):
		super().__init__(market, "OneInAllOut", start_capital)

		if len(params) != 4 or params is None:
			params = [1.0, 0.0, 0.5, -2.0]

		self.n_stock_mov = int(params[0])
		self.buy_perc = params[1]
		self.sell_perc = params[2]
		self.time_comp = int(params[3])
		self.buyed_price: dict = {stock.name: [] for stock in self.market.stocks}

	def avg_stock_price(self, name: str) -> float:
		return (sum(self.buyed_price[name]) / len(self.buyed_price[name])) if len(self.buyed_price[name]) > 0 else 0

	def buy_sell(self, stock: Stock) -> tuple[int, int]:

		# if self.tick_count % (-self.time_comp) == 0 and self.portfolio[stock.name] > 0:
		#	return 0, self.portfolio[stock.name]

		if stock.price() + (transaction_cost(stock.price()) / self.n_stock_mov) < stock.historical_average(from_time=self.time_comp) * (1 + self.buy_perc):
			self.buyed_price[stock.name].append(stock.price())
			return self.n_stock_mov, 0

		if self.portfolio[stock.name] > 0 and stock.price() - (transaction_cost(stock.price()) / self.portfolio[stock.name]) > self.avg_stock_price(stock.name) * (
				1 + self.sell_perc):
			self.buyed_price[stock.name].clear()
			return 0, self.portfolio[stock.name]
		return 0, 0
