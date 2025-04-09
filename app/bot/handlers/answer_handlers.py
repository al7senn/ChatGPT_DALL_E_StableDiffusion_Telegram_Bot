from app.bot.utils import States, translator, TelegramError, encoding

from app.services.stablediffusion import StableDiffusion
from app.services.openaitools import OpenAiTools

from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import BufferedInputFile

from app.services.db import DataBase, DatabaseError

class AnswerHandlers:
    def __init__(self, database: DataBase, openai: OpenAiTools, stable: StableDiffusion):
        self.database = database
        self.openai = openai
        self.stable = stable

    async def chatgpt_answer_handler(self, message: types.Message, state: FSMContext):
        try:
            button = [[KeyboardButton(text="🔙Back")]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard = button, resize_keyboard=True
            )

            user_id = message.from_user.id

            await self.database.save_message(user_id, "user", message.text, len(encoding.encode(message.text)))

            messages, question_tokens = await self.database.get_messages(user_id)

            answer = await self.openai.get_chatgpt(messages)

            if answer:
                answer_tokens = len(encoding.encode(answer))
                await self.database.save_message(user_id, "assistant", answer, answer_tokens)

                await message.answer(
                    text = answer,
                    reply_markup=reply_markup,
                )
            else:
                await message.answer(
                    text = "❌Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.",
                    reply_markup=reply_markup,
                )

            await state.set_state(States.CHATGPT_STATE)
        except DatabaseError:
            raise DatabaseError
        except Exception as e:
            err = TelegramError(str(e))
            err.output()
            raise err

    async def dall_e_answer_handler(self, message: types.Message, state: FSMContext):
        try:
            button = [[KeyboardButton(text="🔙Back")]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard = button, resize_keyboard=True
            )

            question = message.text
            prompt = await translator.translate(question, targetlang='en')
            answer = await self.openai.get_dalle(prompt.text)

            if answer:
                await message.answer_photo(
                    photo=answer,
                    reply_markup=reply_markup,
                    caption=question,
                )
            else:
                await message.answer(
                    text = "❌Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.",
                    reply_markup=reply_markup,
                )

            await state.set_state(States.DALL_E_STATE)
        except DatabaseError:
            raise DatabaseError
        except Exception as e:
            err = TelegramError(str(e))
            err.output()
            raise err

    async def stable_answer_handler(self, message: types.Message, state: FSMContext):
        try:
            button = [[KeyboardButton(text="🔙Back")]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard = button, resize_keyboard=True
            )

            question = message.text
            prompt = await translator.translate(question, targetlang='en')
            photo = await self.stable.get_stable(prompt.text)

            if photo:
                await message.answer_photo(
                    photo=BufferedInputFile(photo, 'image.jpeg'),
                    reply_markup=reply_markup,
                    caption=question,
                )
            else:
                await message.answer(
                    text = "❌Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.",
                    reply_markup=reply_markup,
                )

            await state.set_state(States.STABLE_STATE)
        except DatabaseError:
            raise DatabaseError
        except Exception as e:
            err = TelegramError(str(e))
            err.output()
            raise err
