import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button

from state import state_config
from handlers import dtf_publisher, habr_publisher
from config import load_config

cfg = load_config('.env')
bot_token = cfg.tg_bot.token

bot = Bot(token=bot_token)
dp = Dispatcher()


async def back_to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


start_dialog = Dialog(
    Window(
        Const('Привет, ты запустил меня, чтобы я тебе отправлял новые новости или публикации с сайта Habr и DTF'),
        Button(Const('Habr'), id='habr_button', on_click=habr_publisher.go_habr_dialog),
        Button(Const('DTF'), id='dtf_button', on_click=dtf_publisher.go_dtf_dialog),
        state=state_config.StartSG.first
    ),
)


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=state_config.StartSG.first,
        mode=StartMode.RESET_STACK,
        data={'first_show': True}
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_routers(start_dialog, habr_publisher.rt, habr_publisher.habr_dialog, dtf_publisher.dtf_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)
