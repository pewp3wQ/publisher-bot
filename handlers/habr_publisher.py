import datetime
import asyncio
import logging

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, User, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Multiselect, Group, ManagedMultiselect, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from state import state_config
from scraps import scraps_process
from redis import redis_process

rt = Router()

logger = logging.getLogger(__name__)

# user_dict = {}


@rt.message()
async def other_message(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    logger.info(f'Сообщение от пользователя было удалено -- {message.text}')


async def check_new_news(dialog_manger: DialogManager, bot: Bot, event_from_user: User, **kwargs):
    user_data = await redis_process.get_data(event_from_user.id)
    logger.info(f'{event_from_user.id} -- {user_data}')

    # new_news = await scraps_process.get_news(user_dict, event_from_user.id)
    new_news = await scraps_process.get_news(user_data, event_from_user.id)

    logger.info(f'{event_from_user.id} -- {new_news}')
    # print(user_data)

    for news in new_news:
        # if news[0] not in user_dict[event_from_user.id]['view_user_news']:
        if news[0] not in user_data['view_user_news']:
            # [0] - article url
            # [1] - other hub in article
            # [2] - article title
            # [3] - article hub
            # [4] - article description

            news_read_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Читать', callback_data='read_news', url=news[0])]])
            user_data[news[3]]['last_check_in'] = datetime.datetime.utcnow()
            # user_dict[event_from_user.id][news[3]]['last_check_in'] = datetime.datetime.utcnow()

            text = f'Другие хабы: {", ".join([f"{other_hub}" for other_hub in news[2]])}\n\n{news[1]}\n\n{" ".join(news[4])}'

            await bot.send_message(chat_id=event_from_user.id, text=text, reply_markup=news_read_keyboard)
            await asyncio.sleep(5)

            user_data['view_user_news'].append(news[0])
            # user_dict[event_from_user.id]['view_user_news'].append(news[0])
            await redis_process.set_data(event_from_user.id, user_data)
    # print('пошел отыдхать')
    logger.info('пошел отыдхать')
    while True:
        await asyncio.sleep(3600)
        await asyncio.create_task(check_new_news(dialog_manger, bot, event_from_user, **kwargs))

async def subject_keyboard(**kwargs):
    get_all_subjects = scraps_process.subjects_for_menu()

    return {
        'subject': get_all_subjects
    }


async def hubs_keyboard(dialog_manager: DialogManager, **kwargs):
    get_all_hubs = scraps_process.hubs_for_menu(dialog_manager.dialog_data.get("subjects_selection"))
    return {
        'hubs': get_all_hubs
    }

async def subject_selection(callback: CallbackQuery, widget: ManagedMultiselect, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data.update(subjects_selection=widget.get_checked())


async def hub_selection(callback: CallbackQuery, widget: ManagedMultiselect, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data.update(hubs_selection=widget.get_checked())


async def hub_selected(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # Swap the value key to display to the user which topics and hubs he has selected in Russian.
    inverted_sub_dictionary = {}
    inverted_hub_dictionary = {}

    temp_subject_list = await subject_keyboard()
    temp_subject_list = temp_subject_list['subject']

    temp_hub_list = scraps_process.hubs_for_menu(dialog_manager.dialog_data.get("subjects_selection"))

    for sub in temp_subject_list:
        inverted_sub_dictionary[sub[1]] = sub[0]

    for value in temp_hub_list:
        inverted_hub_dictionary[value[1]] = value[0]

    # print('дошел до создания задачи')
    logger.info('дошел до создания задачи')
    asyncio.create_task(check_new_news(dialog_manager, dialog_manager.event.bot, event_from_user))

    hubs = dialog_manager.dialog_data.get('hubs_selection')
    hub_dict = {}


    for hub in hubs:
        time_dict = {'last_check_in': datetime.datetime.utcnow()}
        hub_dict[hub] = time_dict

    hub_dict['view_user_news'] = []
    # user_dict[event_from_user.id] = hub_dict
    # print(hub_dict)

    logger.info(f'HUB SELECTED FUNC -- {hub_dict}')
    await redis_process.set_data(event_from_user.id, hub_dict)

    # return selected subjects and hubs displayed in Russian
    return {
        'subjects_name': ', '.join([inverted_sub_dictionary.get(x) for x in dialog_manager.dialog_data.get("subjects_selection")]),
        'hubs_name': ', '.join([inverted_hub_dictionary.get(x) for x in dialog_manager.dialog_data.get('hubs_selection')])
    }


async def back_to_previous_window(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def ready_for_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def go_habr_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=state_config.HabrSG.first)


habr_dialog = Dialog(
    Window(
        Const('Отлично, ты вабрал сайт Habr\n'),
        Const('Выбери темы, которые тебе интересны'),
        Group(
            Multiselect(
                checked_text=Format('>>> {item[0]}'),
                unchecked_text=Format('{item[0]}'),
                id='subj',
                item_id_getter=lambda x: x[1],
                items='subject',
                on_state_changed=subject_selection
            ),
            width=1
        ),
        Row(
            Button(Const('Назад'), id='back_habr_dialog', on_click=back_to_menu),
            Button(Const('Далее'), id='habr_next_button', on_click=ready_for_next)
        ),
        state=state_config.HabrSG.first,
        getter=subject_keyboard
    ),
    Window(
        Const('Отлично, ты вабрал темы\n'),
        Const('Теперь выбери Хабы из которых хочешь получать новости'),
        ScrollingGroup(
            Multiselect(
                checked_text=Format('>>> {item[0]}'),
                unchecked_text=Format('{item[0]}'),
                id='hub',
                item_id_getter=lambda x: x[1],
                items='hubs',
                on_state_changed=hub_selection,
            ),
            id='hubs',
            width=1,
            height=10,
        ),
        Row(
            Button(Const('Назад'), id='back_habr_dialog', on_click=back_to_previous_window),
            Button(Const('Далее'), id='habr_next_button', on_click=ready_for_next)
        ),
        state=state_config.HabrSG.second,
        getter=hubs_keyboard
    ),
    Window(
        Const('Отлично, ты вабрал темы\n'),
        Format('Твои выбранные темы: {subjects_name}\n'),
        Format('Твои выбранные хабы: {hubs_name}'),
        state=state_config.HabrSG.third,
        getter=hub_selected
    ),
)
