from collections import defaultdict
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from main_ai import main_mistral
from settings import BOT_KEY, ADMIN_ID

# Проверка корректности токена
if not BOT_KEY or BOT_KEY.isspace():
    raise ValueError("Bot token (BOT_KEY) не задан или некорректный!")

TOKEN = BOT_KEY

# Ограничения на количество сообщений для разных пользователей
OWNER_ID = ADMIN_ID  # Telegram ID администратора
MEMORY_LIMIT_OWNER = 150
MEMORY_LIMIT_OTHERS = 25

# Создать память пользователей
user_memory = defaultdict(list)

dp = Dispatcher()

# Создаем клавиатуру для кнопок
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Очистить память бота")],  # Кнопка для очистки памяти
    ],
    resize_keyboard=True  # Чтобы клавиатура подстраивалась под экран
)


# Функция для добавления сообщений в память
def add_message_to_memory(user_id, role, content):
    limit = MEMORY_LIMIT_OWNER if user_id == OWNER_ID else MEMORY_LIMIT_OTHERS
    user_memory[user_id].append({"role": role, "content": content})

    # Удаляем старые сообщения, если превышен лимит
    if len(user_memory[user_id]) > limit:
        user_memory[user_id].pop(0)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! "
        "Я бот ChatGPT, готов ответить на ваши вопросы.",
        reply_markup=menu_keyboard  # Отправляем клавиатуру при старте
    )
    # Обновить память (начало нового диалога)
    user_memory[message.from_user.id] = []  # Очистка контекста


@dp.message(Command(commands=["clear"]))
async def clear_memory_handler(message: Message) -> None:
    """Команда /clear для очистки памяти пользователя."""
    user_id = message.from_user.id
    if user_id in user_memory:
        user_memory.pop(user_id)  # Удаляем данные из памяти
        await message.answer("Ваша память успешно очищена! 🧹", reply_markup=menu_keyboard)
    else:
        await message.answer("Ваша память уже пуста!", reply_markup=menu_keyboard)


@dp.message(lambda message: message.text == "Очистить память бота")
async def clear_memory_button_handler(message: Message) -> None:
    """Обработка нажатия кнопки для очистки памяти."""
    user_id = message.from_user.id
    if user_id in user_memory:
        user_memory.pop(user_id)  # Очищаем память пользователя
        await message.answer("Память успешно очищена! 🧹", reply_markup=menu_keyboard)
    else:
        await message.answer("Ваша память уже пуста!", reply_markup=menu_keyboard)


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        content = message.text

        # Добавить сообщение пользователя в память
        add_message_to_memory(user_id, "user", content)

        # Уведомить, что бот "печатает"
        bot = message.bot
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # Передать всю историю сообщений в AI
        res = await main_mistral(user_memory[user_id])

        # Добавить ответ AI в память
        add_message_to_memory(user_id, "assistant", res)

        # Ответить пользователю
        await message.answer(res, reply_markup=menu_keyboard)

    except KeyError:
        logging.error("KeyError: user_memory не содержит данных для пользователя.")
        await message.answer("К сожалению, произошла ошибка. Попробуйте снова.", reply_markup=menu_keyboard)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await message.answer("Произошла ошибка при обработке сообщения.", reply_markup=menu_keyboard)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Настройка логирования для удобного отладки
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Бот запущен...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
