import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button

from state import state_config
from handlers import habr_publisher
from config import load_config

cfg = load_config('.env')
bot_token = cfg.tg_bot.token

bot = Bot(token=bot_token)
dp = Dispatcher()


async def back_to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=state_config.HabrSG.first,
        mode=StartMode.RESET_STACK
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_routers(habr_publisher.rt, habr_publisher.habr_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)
