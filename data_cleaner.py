import os

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


def scrape(dir_to_save: str, quote: str):
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

	x: list = []
	y: list = []
	for d in chart:
		x.append(d['x'])
		y.append(d['y'])

	# dir_to_save = "./scenarios/daily/2024-10-18/"

	if not os.path.exists(dir_to_save):
		os.makedirs(dir_to_save)

	with open(f"{dir_to_save}{quote}", "w+") as file:
		file.writelines([f"{v}\n" for v in y])

	print(f"wrote {len(y)} values")


if __name__ == '__main__':
	#clean()
	scrape("./scenarios/daily/2024-10-18/", "msft")
