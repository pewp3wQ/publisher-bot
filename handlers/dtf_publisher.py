from aiogram.types import CallbackQuery, User
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Multiselect, ManagedMultiselect, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from state import state_config
from scraps import scraps_process


async def subsite_keyboard(**kwargs):
    get_all_subsite = scraps_process.subsite_for_menu()

    return {
        'subsite': get_all_subsite
    }


async def subsite_selection(callback: CallbackQuery, widget: ManagedMultiselect, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data.update(subsites_selection=widget.get_checked())


async def subsite_selected(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    inverted_subsite_dictionary = {}

    temp_subiste_list = scraps_process.subsite_for_menu()

    for subsite in temp_subiste_list:
        inverted_subsite_dictionary[subsite[1]] = subsite[0]

    return {
        'subsite_name': ', '.join([inverted_subsite_dictionary.get(x) for x in dialog_manager.dialog_data.get("subsites_selection")])
    }


async def back_to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def ready_for_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def go_dtf_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=state_config.DtfSG.first,  mode=StartMode.RESET_STACK)


dtf_dialog = Dialog(
    Window(
        Const(text='Отлично, ты вабрал сайт DTF\n'),
        Const(text='Выбери темы, которые тебе интересны'),
        ScrollingGroup(
            Multiselect(
                checked_text=Format('>>> {item[0]}'),
                unchecked_text=Format('{item[0]}'),
                id='sub',
                item_id_getter=lambda x: x[1],
                items='subsite',
                on_state_changed=subsite_selection
            ),
            id='subsite',
            width=1,
            height=10,
        ),
        Row(
            Button(Const('Назад'), id='back_dtf_dialog', on_click=back_to_menu),
            Button(Const('Далее'), id='dtf_next_button', on_click=ready_for_next)),
        state=state_config.DtfSG.first,
        getter=subsite_keyboard
    ),
    Window(
        Const('Отлично, ты вабрал темы\n'),
        Format('Твои выбранные темы: {subsite_name}\n'),
        state=state_config.DtfSG.second,
        getter=subsite_selected
    ),
)

