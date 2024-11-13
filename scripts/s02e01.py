import os
import whisper
import sys
import openai
import httpx

from pathlib import Path


system_prompt = f"""
Kontekst: Analizujemy zeznania świadków dotyczące profesora Andrzeja Maja, który wykłada na pewnej uczelni. Zeznania pochodzą od kilku osób, w tym Rafała, który miał bliskie kontakty z profesorem. Część świadków może się mylić lub podawać niespójne informacje. 

Pytanie: Na jakiej ulicy znajduje się instytut uczelni, gdzie wykłada profesor Maj?

Przemyśl to krok po kroku:
1. Jakie instytuty/wydziały na polskich uczelniach mogą być związane z badaniami prowadzonymi przez prof. Maja?
2. Gdzie znajdują się główne siedziby tych instytutów?  
3. Które z tych lokalizacji najlepiej pasują do kontekstu zeznań świadków?
4. Które szczegóły z zeznań mogą potwierdzać lub wykluczać konkretne lokalizacje?
5. Na podstawie powyższej analizy - jaka jest najbardziej prawdopodobna lokalizacja instytutu?

Pamiętaj:
- Rafał jest wiarygodnym źródłem informacji o profesorze
- Weź pod uwagę wszystkie wskazówki z zeznań, nawet jeśli wydają się niespójne
- Szukamy konkretnej nazwy ulicy
"""


if sys.argv[1] == "transcribe":
    files = [Path(root).absolute() / file for root, _, files in os.walk("data/audio/") for file in files]
    model = whisper.load_model("turbo")

    transcripts = [
        model.transcribe(audio=str(file), verbose=False)
        for file in files
    ]

    for i, transcript in enumerate(transcripts):
        with open(f"data/transcripts/{i}.txt", "w") as f:
            f.write(transcript.get("text"))


if sys.argv[1] == "analyze":
    from dotenv import load_dotenv
    load_dotenv()

    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

    files = [Path(root).absolute() / file for root, _, files in os.walk("data/transcripts/") for file in files]

    user_messages = []

    for file in files:
        with open(file, "r") as f:
            user_messages.append({
                "role": "user",
                "content": f.read()
            })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, *user_messages],
    )

    print(response.choices[0])

if sys.argv[1] == "respond":
    from dotenv import load_dotenv
    from aidevs3.poligon import send
    load_dotenv()

    response = sys.argv[2]
    url = f"{os.getenv("AG3NTS_CENTRALA_URL")}/report"
    res = send(url, "mp3", os.getenv("AG3NTS_API_KEY"), response)
    print(res)