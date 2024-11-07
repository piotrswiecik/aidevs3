import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe
from langfuse.openai import openai

from aidevs3.data_repair import DataRepairParser
from aidevs3.poligon import send

load_dotenv()

key = os.environ.get("AG3NTS_API_KEY")
url_base = os.environ.get("AG3NTS_CENTRALA_URL")
file_origin_url = f"{url_base}/data/{key}/json.txt"
verification_url = f"{url_base}/report"

langfuse = Langfuse(
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    host=os.environ.get("LANGFUSE_HOST"),
)


@observe()
def main():
    logging.basicConfig(level=logging.INFO)

    if not os.path.exists("parsed_data.json"):
        parser = DataRepairParser(file_origin_url)
        repaired = parser.repair()
        parsed = parser.prepare_for_verification(repaired)
        with open("parsed_data.json", "w") as f:
            f.write(parsed)
    else:
        logging.info("Using cached data")
        parsed = open("parsed_data.json").read()

    res = send(verification_url, task="JSON", apikey=key, answer=json.loads(parsed))
    print(res)


if __name__ == "__main__":
    main()
