from aiogram.fsm.state import StatesGroup, State

class SendAdState(StatesGroup):
    message = State()
    ready = State()
