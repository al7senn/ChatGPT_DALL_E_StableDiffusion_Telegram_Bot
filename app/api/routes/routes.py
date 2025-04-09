from aiogram import Bot, Dispatcher, types
from fastapi import Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import ValidationError

from app.api.models import PaymentsRequestModel
from app.bot.utils import TelegramError
from app.services.cryptopay import CryptoPayError
from app.services.db import DataBase, DatabaseError
from app.services.payment_successful import payment_success

import logging

class Handlers:
    def __init__(self, database: DataBase, dp: Dispatcher, bot: Bot):
        self.database = database
        self.dp = dp
        self.bot = bot

    async def payments_webhook(self, request: Request) -> PlainTextResponse:
        try:
            validated_data = PaymentsRequestModel(** await request.json())
            await payment_success(
                self.bot,
                self.database,
                validated_data.update_type,
                validated_data.payload.invoice_id
            )
            return PlainTextResponse('OK', status_code=200)
        except ValidationError:
            return PlainTextResponse('Wrong request', status_code=400)
        except DatabaseError:
            return PlainTextResponse('Database Error', status_code=500)
        except TelegramError:
            return PlainTextResponse('Telegram Error', status_code=500)
        except Exception as e:
            logging.exception(e)
            return PlainTextResponse('Error', status_code=500)

    async def bot_webhook(self, request: Request) -> JSONResponse:
        try:
            data = await request.json()
            update = types.Update(**data)
            await self.dp.feed_update(self.bot, update)
            return JSONResponse({"status": "ok"})
        except Exception as e:
            logging.exception(e)
            return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)
