import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from openai import OpenAI


@dataclass
class Question:
    question: str
    answer: int | str


@dataclass
class DataRepairParser:
    origin_url: str
    cache_path: Optional[Path] = Path("data.json")

    def __post_init__(self) -> None:
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._setup_logging()
        self.data = self._load_data()
        self.questions = self.data["test-data"]

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DataRepair system")

    def _load_data(self) -> Dict:
        if self.cache_path and self.cache_path.exists():
            self.logger.info("Loading data from cache")
            return self._load_from_cache()
        return self._load_data_from_remote()

    def _load_from_cache(self) -> Dict:
        return json.loads(self.cache_path.read_text())

    def _load_data_from_remote(self) -> Dict:
        response = httpx.get(self.origin_url)
        response.raise_for_status()
        data = response.json()

        if self.cache_path:
            self.cache_path.write_text(json.dumps(data))

        return data

    def repair(self) -> List[Dict]:
        repaired = []
        pattern = r'{"question":\s*"(\d+)\s*([+\-*/])\s*(\d+)",\s*"answer":\s*(\d+)}'
        for question in self.questions:
            # Is the question standard math or a special case?
            if not re.match(pattern, json.dumps(question)):
                # Special case always goes to LLM for repair
                self.logger.info(f"Found a special case: {question}")
                res = self._send_to_model(
                    question
                )  # TODO: we're not checking what comes back
                self.logger.info(f"Repaired special case: {res}")
                repaired.append(res)
            else:
                # Is the math question correct?
                q, a = question["question"], question["answer"]
                if eval(q) == a:
                    repaired.append(question)
                else:
                    # Repair the math question
                    self.logger.info(f"Found a broken math question: {question}")
                    res = self._send_to_model(question)
                    self.logger.info(f"Repaired math question: {res}")
                    repaired.append(res)

        return repaired

    def _send_to_model(self, question: Dict) -> str:
        system_prompt = """
        <objective>
        You are supposed to analyze pairs of questions and answers and provide correct answers or fix mistakes.
        Data will be provided as list of JSON formatted objects. Question is marked as "question" or "q" and answer is marked as "answer" or "a".
        Sometimes data can have nested structures, but you should always look for the "question" or "q" and "answer" and "a" keys.
        </objective>
        <rules>
        - If question is a math operation, set answer field to correct number.
        - If question is not a math operation, set answer field to correct string.
        - If answer is incorrect, provide the correct answer. 
        - If answer is correct just return the data as is.
        - You MUST ALWAYS return the data in the same format as it was provided.
        </rules>
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Repair these questions: {json.dumps(question)}",
                    },
                ],
            )
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f"Error in AI data repair: {str(e)}")
            raise e

    def prepare_for_verification(self, data: List[Dict]) -> str:
        return json.dumps(
            {
                "apikey": os.environ.get("AG3NTS_API_KEY"),
                "description": self.data["description"],
                "copyright": self.data["copyright"],
                "test-data": data,
            }
        )
