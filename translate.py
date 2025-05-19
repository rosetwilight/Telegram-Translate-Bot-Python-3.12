import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from googletrans import Translator
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
translator = Translator()
user_modes = {}

def language_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 Англ → Рус", callback_data="en-ru"),
            InlineKeyboardButton(text="🇷🇺 Рус → Англ", callback_data="ru-en")
        ]
    ])
    return kb

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_modes[message.from_user.id] = "en-ru"
    await message.answer(
        "Приветик, мой переводчик готов 😘\nВыбери направление:",
        reply_markup=language_menu()
    )

@dp.callback_query(F.data.in_({"en-ru", "ru-en"}))
async def language_callback(callback: types.CallbackQuery):
    current = user_modes.get(callback.from_user.id)

    # Если пользователь уже выбрал этот режим — просто ответим и ничего не меняем
    if current == callback.data:
        await callback.answer("Уже выбран этот режим 😘", show_alert=False)
        return

    # Обновляем режим и отвечаем
    user_modes[callback.from_user.id] = callback.data
    await callback.answer(f"Теперь перевожу: {callback.data.replace('-', ' → ')}")

    # Меняем клавиатуру только если это необходимо
    try:
        await callback.message.edit_reply_markup(reply_markup=language_menu())
    except Exception as e:
        # Telegram может всё ещё ругаться — на всякий случай ловим исключение
        print(f"⚠️ Не удалось обновить клавиатуру: {e}")


@dp.message(F.text)
async def translate_message(message: Message):
    mode = user_modes.get(message.from_user.id, "en-ru")
    src, dest = mode.split('-')
    try:
        result = translator.translate(message.text, src=src, dest=dest)
        await message.reply(f"🔤 Перевод:\n{result.text}")
    except Exception:
        await message.reply("Ой, что-то пошло не так, мой котик... попробуй снова 🥺")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
