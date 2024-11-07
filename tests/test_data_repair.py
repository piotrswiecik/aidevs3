import logging
from dotenv import load_dotenv
import os

from aidevs3.data_repair import DataRepairParser

load_dotenv()

key = os.environ.get("AG3NTS_API_KEY")
url_base = os.environ.get("AG3NTS_CENTRALA_URL")
file_origin_url = f"{url_base}/data/{key}/json.txt"
verification_url = f"{url_base}/report"

def test_is_math_question():
    parser = DataRepairParser(file_origin_url, verification_url)
    assert parser._is_simple_question({"question": "2 + 2", "answer": 4})
    assert not parser._is_simple_question({"question": "What is the capital of France?", "answer": "Paris"})
    assert not parser._is_simple_question({"question": "2 ++ 2", "answer": "4"})