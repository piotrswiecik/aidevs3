import os
import httpx
from dotenv import load_dotenv

from aidevs3.services.ai_service import CompletionMessage, LocalLlamaService, OllamaCompletionRequest
from aidevs3.poligon import send

load_dotenv()

task_url = f"{os.getenv("AG3NTS_CENTRALA_URL")}/data/{os.getenv("AG3NTS_API_KEY")}/cenzura.txt"
task_response = httpx.get(task_url)

print(task_response.text)

llama = LocalLlamaService()

system_prompt = """
Tekst, który otrzymasz od użytkownika zawiera wrażliwe dane osobowe. Twoim zadaniem jest zastąpienie wszystkich wrażliwych danych osobowych słowem „CENZURA” i niczym innym. Upewnij się, że absolutnie każde imię, nazwisko, miasto, ulica, numer domu/mieszkania, wiek oraz PESEL są zawsze zamienione na „CENZURA”.

KRYTYCZNE ZASADY:

Zawsze zamieniaj pełne imię i nazwisko na „CENZURA”. Nie pomijaj ani imienia, ani nazwiska. Jeśli pojawia się imię lub nazwisko, bezwzględnie zamień je na „CENZURA”.
Nigdy nie zmieniaj żadnych innych słów ani znaków. Zachowaj każdą kropkę, przecinek, spację i każdą literę poza danymi osobowymi.
Nigdy nie usuwaj ani nie dodawaj żadnych znaków. Zostaw cały tekst poza danymi osobowymi bez zmian.
Zastępuj słowem „CENZURA” wyłącznie:

Imię i nazwisko (np. „Jan Kowalski” to CENZURA lub „Kowalski” to CENZURA - zawsze zamieniaj pełne imię i nazwisko na jedno wystąpienieCENZURA)
Nazwę miasta
Nazwę ulicy oraz numer domu/mieszkania
Wiek osoby
Numer PESEL
PRZYKŁADY: IN: „Osoba podejrzana to Andrzej Mazur. Adres: Gdańsk, ul. Długa 8. Wiek: 29 lat.” OUT: „Osoba podejrzana to CENZURA. Adres: CENZURA, ul. CENZURA. Wiek: CENZURA lat.”

IN: „Podejrzany, Piotr Nowak, zamieszkały w Krakowie, ul. Zielona 5. Ma 35 lat.” OUT: „Podejrzany, CENZURA, zamieszkały w CENZURA, ul. CENZURA. Ma CENZURA lat.”

Pamiętaj: Nie zmieniaj żadnej części tekstu poza danymi osobowymi. Wszystko poza danymi osobowymi pozostaje niezmienione.
"""

user_prompt = task_response.text

request = OllamaCompletionRequest(
    messages=[
        CompletionMessage(role="system", content=system_prompt),
        CompletionMessage(role="user", content=user_prompt),
    ],
    model="gemma2:latest",
)

solution = llama.completion(request)
print(solution)

verification_url = f"{os.getenv("AG3NTS_CENTRALA_URL")}/report"
res = send(verification_url, task="CENZURA", apikey=os.getenv("AG3NTS_API_KEY"), answer=solution.encode("utf-8"))

print(res)
