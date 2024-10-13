import os


def clean():
	dir_to_clean = "./to_clean"
	dir_clean = "./clean"
	for file in os.listdir(dir_to_clean):
		print(f"cleaning {file}")
		with open(f"{dir_to_clean}/{file}", "r") as f:
			past = [line.rstrip().split(",")[1].replace("$", '') + "\n" for line in f.readlines()[1:]]
		past.reverse()
		with open(f"{dir_clean}/{file[:-4]}", "w+") as f:
			f.writelines(past)
		print(f"\tcleaned {file}")


if __name__ == '__main__':
	clean()
