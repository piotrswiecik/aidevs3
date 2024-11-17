import base64
from collections import defaultdict
from enum import Enum
import logging
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_openai import AzureChatOpenAI
from openai import OpenAI

from aidevs3.services.ai_service import OpenAIService


def segregate_files(dir_path: Path) -> Dict[str, List[Path]]:
    out = defaultdict(list)
    for file in dir_path.iterdir():
        if file.suffix == ".txt":
            out["txt"].append(file)
        elif file.suffix == ".png":
            out["png"].append(file)
        elif file.suffix == ".mp3":
            out["mp3"].append(file)
    return out


class Outcome(str, Enum):
    PEOPLE = "people"
    HARDWARE = "hardware"
    OTHER = "other"


FileName = str


def process_text(text) -> Outcome:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
    Jesteś asystentem analizującym raporty z fabryki w celu ich klasyfikacji do jednej z trzech kategorii: 'ludzie', 'sprzęt', lub 'inne'.

    Zasady klasyfikacji:
    'ludzie': Raporty opisujące incydenty bezpieczeństwa związane z działalnością człowieka. Pomijaj inne istoty żywe (np. zwierzęta).
    'sprzęt': Raporty opisujące incydenty związane z funkcjonowaniem sprzętu (hardware).
    'inne': Raporty dotyczące innych tematów, w tym incydentów oprogramowania (software).
    Wymagania dotyczące odpowiedzi:
    Twoja odpowiedź musi być jednym słowem: 'ludzie', 'sprzęt', lub 'inne'.

    Przykłady:
    'ludzie': "Wykryto intruza na terenie fabryki. Zidentyfikowano go."
    'inne': "Wykryto intruza na terenie fabryki. Okazało się że to dzik."
    'sprzęt': "Wykryto uszkodzenie taśmy produkcyjnej. Naprawiono ją."
    'inne': "Ludzie pracujący w fabryce są niezadowoleni z warunków pracy. Zgłoszono to do zarządu."
    'sprzęt': "Przeprowadzono remont maszyn produkcyjnych których wydajność spadła."
    'inne': "Wgrano nową wersję programu do sterowania maszynami produkcyjnymi."
    'inne': "Zmieniono harmonogram pracy w fabryce."
    'inne': "Z pracy w fabryce zwolniono kilku pracowników."
    'inne': "Przeprowadzono kontrolę maszyn produkcyjnych."
    'sprzęt': "Przeprowadzono kontrolę maszyn produkcyjnych i wykryto uszkodzenie jednej z nich."
    """

    user_prompt = f"""
    Przeanalizuj ten raport zgodnie z wytycznymi:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    classification = response.choices[0].message.content

    match classification:
        case "ludzie":
            return Outcome.PEOPLE
        case "sprzęt":
            return Outcome.HARDWARE
        case "inne":
            return Outcome.OTHER
        case _:
            logging.error(f"OpenAI response: {response}")


def eval_process_text(prompt: str, options, context):
    """To be used by Promptfoo evaluation."""
    processed = process_text(prompt)
    return {"output": processed}


def image_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def process_image(path) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = f"""
    Jesteś asystentem analizującym raporty z fabryki.
    
    Raporty są dostarczane w postaci graficznej. Twoim zadaniem jest ekstracja tekstu z obrazu.
    Przeanalizuj dokładnie obraz i zwróć odpowiedź w formie tekstu pomijając formatowanie.
    """

    user_prompt = f"""
    Raport do przeanalizowania.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_b64(path)}",
                }},
            ]},
        ],
    )
    return response.choices[0].message.content

def process_audio(path) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    with open(path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcript


def process_file(file_type, path) -> Tuple[Outcome, FileName]:
    if file_type == "txt":
        with open(path, "r") as f:
            text = f.read()
        outcome = process_text(text)
        print(f"Done processing text file {path}, classification: {outcome}")
        return (outcome, path.name)
    if file_type == "png":
        extracted_text = process_image(path)
        outcome = process_text(extracted_text)
        print(f"Done processing image file {path}, classification: {outcome}")
        return (outcome, path.name)
    if file_type == "mp3":
        extracted_text = process_audio(path)
        outcome = process_text(extracted_text)
        print(f"Done processing audio file {path}, classification: {outcome}")
        return (outcome, path.name)


if __name__ == "__main__":
    load_dotenv()

    if len(sys.argv) < 2:
        print("Using default path")
        path = Path("data/pliki_z_fabryki")
    else:
        path = Path(sys.argv[1])

    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)
    if not path.is_dir():
        print(f"Path {path} is not a directory")
        sys.exit(1)

    results = defaultdict(list)
    for file_type, list_of_paths in segregate_files(path).items():
        for file_path in list_of_paths:
            print(f"Processing {file_type}: {file_path}")
            outcome, file_name = process_file(file_type, file_path)
            if outcome is not None:
                results[outcome.value].append(file_name)
                print(f"Results updated - new {outcome.value} entry")
    
    import pickle
    with open("results.pkl", "wb") as f:
        pickle.dump(results, f)
    print(results)

    