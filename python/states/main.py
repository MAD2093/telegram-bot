from aiogram.fsm.state import StatesGroup, State

class FilterStates(StatesGroup):
    edit_spread = State()
    edit_profit = State()
    edit_volume = State()
    edit_fee = State()
    edit_daily_turnover = State()
    custom_frequency = State()

class BlacklistStates(StatesGroup):
    add_coin = State()
    remove_coin = State()
    add_net = State()
    remove_net = State()


