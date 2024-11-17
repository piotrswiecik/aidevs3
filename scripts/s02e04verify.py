import pickle
import os
from pprint import pprint

from aidevs3.poligon import send

print(os.getcwd())

with open("results.pkl", "rb") as f:
    results = pickle.load(f)

del results["other"]
pprint(results)

url = f"{os.getenv("AG3NTS_CENTRALA_URL")}/report"
key = os.getenv("AG3NTS_API_KEY")
res = send(url, apikey=key, task="kategorie", answer=results)
print(res)