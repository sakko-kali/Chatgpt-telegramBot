from collections import defaultdict
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from main_ai import main_mistral
from settings import BOT_KEY, ADMIN_ID

TOKEN = BOT_KEY

# Ограничения на количество сообщений для разных пользователей
OWNER_ID = ADMIN_ID  # Замените на ваш Telegram ID
MEMORY_LIMIT_OWNER = 150
MEMORY_LIMIT_OTHERS = 25

# Создать память пользователей
user_memory = defaultdict(list)

dp = Dispatcher()


# Функция для добавления сообщений в память
def add_message_to_memory(user_id, role, content):
    limit = MEMORY_LIMIT_OWNER if user_id == OWNER_ID else MEMORY_LIMIT_OTHERS
    user_memory[user_id].append({"role": role, "content": content})

    # Удаляем старые сообщения, если превышен лимит
    if len(user_memory[user_id]) > limit:
        user_memory[user_id].pop(0)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
    # Обновить память (начало нового диалога)
    user_memory[message.from_user.id] = []  # Очистка контекста


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        content = message.text

        # Добавить сообщение пользователя в память
        add_message_to_memory(user_id, "user", content)

        # Передать всю историю сообщений в AI
        res = await main_mistral(user_memory[user_id])

        # Добавить ответ AI в память
        add_message_to_memory(user_id, "assistant", res)

        # Ответить пользователю
        await message.answer(res)

    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
