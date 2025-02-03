import asyncio
from mistralai import Mistral
from settings import APIKEY


async def main_mistral(messages):
    mistral = Mistral(api_key=APIKEY.strip())

    try:
        res = await mistral.chat.complete_async(
            model="mistral-small-latest",
            messages=messages,  # Передаем список сообщений
            stream=False
        )

        # Убедимся, что структура ответа корректна
        if not res.choices or not res.choices[0].message.content:
            raise ValueError("Invalid or empty response received from API")

        # Возвращаем содержимое первого сообщения
        return res.choices[0].message.content

    except Exception as e:
        # Обработка ошибок
        print(f"An error occurred: {e}")
        return "Произошла ошибка при обработке запроса."



# Example of calling the async main function
if __name__ == "__main__":
    content = "Hello! Can you explain the asynchronous usage of APIs?"
    result = asyncio.run(main_mistral(content))
    print(result)
