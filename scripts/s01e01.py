import asyncio
import httpx
from aidevs3.captcha import extract_question, answer_question


async def main():
    url = "https://xyz.ag3nts.org/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

            question = await extract_question(response.text)
            if not question:
                print("No question found in the content")
                return

            answer = await answer_question(question)

            login_response = await client.post(
                url,
                data={"username": "tester", "password": "574e112a", "answer": answer},
            )

            print(f"question: {question}")
            print(f"answer: {answer}")
            print(login_response.content)

    except httpx.ConnectError:
        print(f"Failed to connect to {url}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
