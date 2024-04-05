from aiogram.fsm.state import State, StatesGroup


class StartSG(StatesGroup):
    first = State()


class HabrSG(StatesGroup):
    first = State()
    second = State()
    third = State()
