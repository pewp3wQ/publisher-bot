import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from aiogram_dialog.widgets.kbd import Button

from state import state_config
from handlers import habr_publisher
from config import load_config

cfg = load_config('.env')
bot_token = cfg.tg_bot.token

bot = Bot(token=bot_token)
dp = Dispatcher()


async def back_to_menu1(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=state_config.HabrSG.first,
        mode=StartMode.RESET_STACK
    )


@dp.message()
async def other_message(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    logger = logging.getLogger(__name__)
    logger.info(f'Сообщение от пользователя было удалено -- {message.text}')


if __name__ == '__main__':
    logging.basicConfig(filename='../publisher-bot/bots.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8')
    dp.include_routers(habr_publisher.rt, habr_publisher.habr_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)
