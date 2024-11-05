from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def extract_question(page_content: str) -> str:
    prompt = f"""
    Parse this website content and extract a question.
    There is only one question in the content.
    The question should be a single sentence.
    If there is no question, return an empty string.

    Content:
    {page_content}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
    )

    return response.choices[0].message.content


async def answer_question(question: str) -> str:
    prompt = f"""
    Answer the question. The answer is a single integer number.
    Provide the answer only, without any other text, numbers, or characters.
    If you cannot answer the question, return 0.
    Question: {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
    )

    return response.choices[0].message.content