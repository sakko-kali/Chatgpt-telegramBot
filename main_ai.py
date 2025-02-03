import logging
from mistralai import Mistral
from settings import APIKEY


async def main_mistral(messages):
    # Проверка входных данных
    if not isinstance(messages, list) or not messages:
        raise ValueError("Messages must be a non-empty list of dictionaries.")

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

    except ValueError as ve:
        logging.error(f"Validation error: {ve}")
        return "Ошибка: Неверный запрос. Проверьте данные."

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Извините, произошла ошибка при обработке запроса."


# Пример вызова основной функции (для тестирования)
if __name__ == "__main__":
    import asyncio

    test_messages = [{"role": "user", "content": "Привет! Расскажи, как работает API."}]
    result = asyncio.run(main_mistral(test_messages))
    print(result)
