import random
import typing

import numpy as np
from matplotlib import pyplot as plt


class Stock:
	def __init__(self, name: str, past: list = None):
		if past is None:
			past = []

		self.name: str = name
		self.past: list = past

	def price(self) -> float:
		return self.past[-1]

	def historical_average(self, from_time: int = 0, to_time: int = -1) -> float:
		return sum(self.past[from_time:to_time]) / len(self.past[from_time:to_time])

	def historical_min(self, from_time: int = 0, to_time: int = -1) -> float:
		return min(self.past[from_time:to_time])

	def historical_max(self, from_time: int = 0, to_time: int = -1) -> float:
		return max(self.past[from_time:to_time])

	def trend(self, from_time: int = -2, to_time: int = -1) -> float:
		index1 = from_time if from_time > 0 else len(self.past) + from_time
		index2 = to_time if to_time > 0 else len(self.past) + to_time
		return ((self.past[from_time] - self.past[to_time]) / (index1 - index2)) if len(self.past) > 0 and index1 != index2 else 0

	def json(self, include_past: bool = True) -> dict[str: typing.Any]:
		js = {'name': self.name, 'price': self.past[-1]}
		if include_past:
			js['past'] = self.past

		return js

	def __str__(self):
		return str(self.json())


class Market:

	def __init__(self):
		self.stocks: list = []

	def add_stock(self, stk: Stock) -> None:
		self.stocks.append(stk)

	def all_pasts(self) -> list[list]:
		return [s.past for s in self.stocks]

	def history_len(self) -> int:
		return len(self.stocks[0].past)

	def stock_by_name(self, name: str) -> Stock | None:
		for stock in self.stocks:
			if stock.name == name:
				return stock
		return None

	def gen_fig(self, names: list[str] = None, fig_index: int = 0) -> plt.Figure:
		stocks_to_plot = []

		if len(names) == 0 or names is None:
			stocks_to_plot = self.stocks
		else:
			for s in self.stocks:
				if s.name in names:
					stocks_to_plot.append(s)

		time_len = self.history_len()
		t = np.arange(0, time_len)

		fig = plt.figure(fig_index)
		ax = fig.subplots()
		for s in stocks_to_plot:
			ax.plot(t, s.past, label=s.name)
		fig.legend(loc="center right")
		fig.set_figwidth(10)
		return fig


class SimStock(Stock):
	def __init__(self, i=0):
		super().__init__(f"sim-{i}", [random.randint(10, 500)])
		self.trend = random.uniform(6, -6)
		self.stability = random.uniform(2, -2)

	def json(self, include_past=False) -> dict[str: typing.Any]:
		json = super(SimStock, self).json(include_past)
		json['trend'] = self.trend
		json['stability'] = self.stability
		return json


class SimMarket(Market):
	def __init__(self, past_time_len=100, n_stocks=2):
		super().__init__()
		self.new_past(past_time_len, n_stocks)

	def new_past(self, past_time_len, n_stocks) -> None:
		self.stocks = [SimStock(i) for i in range(n_stocks)]
		self.time_forward(past_time_len)

	def time_forward(self, time) -> None:
		for stock in self.stocks:
			print(stock)
			past = stock.past
			for t in range(time):
				mean_fluct = (past[-1] - past[0]) / len(past)
				fluct = mean_fluct * random.uniform(-6, 6) + random.uniform(stock.trend, stock.stability)
				past.append(past[-1] + fluct)


if __name__ == '__main__':
	m = SimMarket()
	m.gen_fig()
	plt.show()
