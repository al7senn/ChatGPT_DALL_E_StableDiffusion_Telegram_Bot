from ..utils import States

from aiogram import types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.fsm.context import FSMContext
from aiogram import F

@dp.message(States.ENTRY_STATE, F.text.regexp(r'^💭Chatting — ChatGPT-4o$'))
@dp.message(States.ENTRY_STATE, F.text.regexp(r'^🌄Image generation — DALL·E 3$'))
@dp.message(States.ENTRY_STATE, F.text.regexp(r'^🌅Image generation — Stable Diffusion 3$'))
async def question_handler(message: types.Message, state: FSMContext):
    button = [[KeyboardButton(text="🔙Back")]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard = button, resize_keyboard=True
    )
    await message.answer(
        text = "Enter your text: 👇🏻",
        reply_markup=reply_markup,
    )
    option = message.text
    if option == "💭Chatting — ChatGPT-4o":
        await state.set_state(States.CHATGPT_STATE)
    elif option == "🌄Image generation — DALL·E 3":
        await state.set_state(States.DALL_E_STATE)
    elif option == "🌅Image generation — Stable Diffusion 3":
        await state.set_state(States.STABLE_STATE)