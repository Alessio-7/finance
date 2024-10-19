import os
from datetime import datetime

import requests as requests


def clean():
	dir_to_clean = "./scenarios/to_clean"
	dir_clean = "./scenarios/current"

	csv_char = ","

	for file in os.listdir(dir_to_clean):
		print(f"cleaning {file}")
		with open(f"{dir_to_clean}/{file}", "r") as f:
			past = [line.rstrip().split(csv_char)[1].replace("$", '') + "\n" for line in f.readlines()[1:]]
		past.reverse()
		with open(f"{dir_clean}/{file[:-4]}", "w+") as f:
			f.writelines(past)
		print(f"\tcleaned {file}")

# time_samples: np.ndarray = np.arange(4 * 60, 16 * 60, 10)


def scrape(dir_to_save: str, quote: str, sample_every_minute: int = 5):
	headers = {
		'accept': 'application/json, text/plain, */*',
		'accept-encoding': 'gzip, deflate, br, zstd',
		'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
		'origin': 'https//www.nasdaq.com',
		'priority': 'u=1, i',
		'referer': 'https://www.nasdaq.com/',
		'sec-ch-ua': '"Not)A;Brand";v="99", "Opera GX";v="113", "Chromium";v="127"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '\"Windows\"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-site',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0'
		}

	resp = requests.get(f"https://api.nasdaq.com/api/quote/{quote.upper()}/chart?assetclass=stocks", headers=headers)
	chart = resp.json()['data']['chart']

	t_samples: list = []
	y: list = []
	for d in chart:
		dateTime = d['z']['dateTime'].split(" ")
		time = [int(hm) for hm in dateTime[0].split(":")]

		if dateTime[1] == "PM":
			time[0] = time[0] + 12

		time_sample = time[0] * 60 + time[1]
		time_sample -= time_sample % sample_every_minute

		if time_sample not in t_samples:
			t_samples.append(time_sample)
			y.append(d['z']['value'])

	# dir_to_save = "./scenarios/daily/2024-10-18/"

	if not os.path.exists(dir_to_save):
		os.makedirs(dir_to_save)

	with open(f"{dir_to_save}/{quote}", "w+") as file:
		file.writelines([f"{v}\n" for v in y])
	with open(f"{dir_to_save}_norm/{quote}", "w+") as file:
		file.writelines([f"{round(float(v) - float(y[0]), 4)}\n" for v in y])

	print(f"wrote {len(y)} values")


if __name__ == '__main__':
	# clean()
	t = datetime.now().strftime("%Y-%m-%d")
	for q in ["msft", "nflx", "tsla", "aapl", "nvda", "amzn"]:
		scrape(f"./scenarios/daily/{t}", quote=q)
