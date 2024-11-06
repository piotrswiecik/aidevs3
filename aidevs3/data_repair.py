import httpx


import json
import logging
import os
import re


class DataRepairParser:
    def __init__(self, origin_url: str, verification_url: str) -> None:
        """
        Args:
            origin_url (str): GET URL to download the JSON data.
            verification_url (str): POST URL to the verification endpoint.
        """
        self._origin_url = origin_url
        self._verification_url = verification_url
        if not os.path.exists("data.json"):
            self._data = self._get_data()
            try:
                self._test_data = self._data["test-data"]
                self._dump_to_file("data.json")
                logging.info("Data loaded from the origin URL and cached to file.")
            except KeyError:
                raise Exception("Error: 'test-data' key not found in the JSON data.")
            except Exception as e:
                raise Exception("Error:", str(e))
        else:
            with open("data.json", "r") as f:
                self._test_data = json.loads(f.read())
                logging.info("Data loaded from cache file.")

    def _get_data(self) -> None:
        res = httpx.get(self._origin_url)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception("Error:", res.status_code)

    def _dump_to_file(self, file_path: str) -> None:
        """Save all test data to json string."""
        with open(file_path, "w") as f:
            f.write(json.dumps(self._test_data))

    def _is_math_question(self, question: dict) -> bool:
        """Verify if question provided as {question: answer} is a math question or open-ended."""
        pattern = r'{"question":\s*"(\d+)\s*([+\-*/])\s*(\d+)",\s*"answer":\s*(\d+)}'
        match = re.match(pattern, json.dumps(question))
        return bool(match)