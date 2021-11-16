import os, csv, random

length = 50

vectors = [[random.random() for _ in range(128)] for _ in range(length)]

with open(f"{os.path.split(os.path.realpath(__file__))[0]}/vectors.csv", "w+") as f:
    writer = csv.writer(f)
    writer.writerow(["vector", "color", "brand"])
    for idx, vector in enumerate(vectors):
        writer.writerow([vector, idx + 2000, idx])
