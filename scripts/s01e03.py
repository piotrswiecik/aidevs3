import logging
import os
from dotenv import load_dotenv

from aidevs3.data_repair import DataRepairParser

load_dotenv()

key = os.environ.get("AG3NTS_API_KEY")
url_base = os.environ.get("AG3NTS_CENTRALA_URL")
file_origin_url = f"{url_base}/data/{key}/json.txt"
verification_url = f"{url_base}/report"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = DataRepairParser(file_origin_url, verification_url)
    print(parser._is_math_question({"question": "2 + 2", "answer": 4}))
