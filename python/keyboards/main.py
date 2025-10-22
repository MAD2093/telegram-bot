from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.consts import *
from database.models import User

def settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Фильтры", callback_data="filters_back")],
        [InlineKeyboardButton(text="🔗 Настройка пары", callback_data="menu_msg"),],
        [InlineKeyboardButton(text="🔄 Частота уведомлений", callback_data="menu_notifys"),],
    ])

def notifys_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 При каждом обновлении", callback_data="freq_instant")],
        [InlineKeyboardButton(text="⏰ Раз в 15 минут", callback_data="freq_15min"), InlineKeyboardButton(text="🕐 Раз в час", callback_data="freq_1hour")],
        [InlineKeyboardButton(text="🚫 Отключить повторы", callback_data="freq_never")],
        [InlineKeyboardButton(text="✏️ Своё значение", callback_data="freq_custom")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu_settings")],
    ])

def msg_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👀 Предпросмотр", callback_data="show_msg")],
        [InlineKeyboardButton(text="⚙️ Настройка параметров", callback_data="edit_params")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu_settings")],
    ])

def show_msg_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="msg_back")],
    ])

def filters_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏦 Биржи", callback_data="edit_exchanges")],
        [InlineKeyboardButton(text="🔀 Спред", callback_data="edit_spread"), InlineKeyboardButton(text="💰 Профит", callback_data="edit_profit")],
        [InlineKeyboardButton(text="📊 Объем", callback_data="edit_volume"), InlineKeyboardButton(text="💸 Комиссия", callback_data="edit_fee")],
        [InlineKeyboardButton(text="📈 24ч. оборот", callback_data="edit_daily_turnover"), InlineKeyboardButton(text="📃 Контракты", callback_data="edit_contract")],
        [InlineKeyboardButton(text="🚫 ЧС", callback_data="edit_blacklists")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu_settings")],
    ])

def blacklist_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 ЧС Монет", callback_data="edit_blacklist_coins")],
        [InlineKeyboardButton(text="🔗 ЧС Сетей", callback_data="edit_blacklist_nets")],
        [InlineKeyboardButton(text="⬅️ Обратно в меню", callback_data="filters_back")]
    ])

def coins_blacklist_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить монеты", callback_data="add_coin")],
        [InlineKeyboardButton(text="➖ Удалить монеты", callback_data="remove_coin")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_blacklists")]
    ])

def nets_blacklist_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить сети", callback_data="add_net")],
        [InlineKeyboardButton(text="➖ Удалить сети", callback_data="remove_net")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_blacklists")]
    ])

def cancel_keyboard(type):
    match type:
        case "edit": 
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
            ])
        case "freq":
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_freq")]
            ])

def get_category_data(category_key: str) -> Tuple[str, List[Tuple[int, str]]]:
    """Возвращает данные категории по ключу"""
    categories = {
        "max_volume_params": ("Максимальный объём", [
            (SPREAD_MAX_BIT, "Спред"),
            (PROFIT_MAX_BIT, "Профит"),
            (COMMISSION_MAX_BIT, "Комиссия"),
        ]),
        "min_volume_params": ("Минимальный объём", [
            (SPREAD_MIN_BIT, "Спред"),
            (PROFIT_MIN_BIT, "Профит"),
            (COMMISSION_MIN_BIT, "Комиссия"),
        ]),
        "additional_params": ("Дополнительные параметры", [
            (CHECK_CONTRACT_BIT, "Проверка контрактов"),
            (DAILY_TURNOVER_BIT, "24ч оборот"),
            (WITHDRAW_TIME_BIT, "Время вывода"),
            (LIFETIME_BIT, "Время жизни"),
        ])
    }
    return categories.get(category_key, ("", []))

def get_category_params(category_key: str) -> List[Tuple[int, str]]:
    """Возвращает список параметров категории"""
    category_data = get_category_data(category_key)
    return category_data[1] if category_data else []

def main_params_keyboard() -> InlineKeyboardMarkup:
    """Генерирует главное меню выбора категории параметров"""
    buttons = [
        [InlineKeyboardButton(
            text=f"📈 Макс объём",
            callback_data="max_volume_params_0"
        )],
        [InlineKeyboardButton(
            text=f"📉 Мин объём", 
            callback_data="min_volume_params_0"
        )],
        [InlineKeyboardButton(
            text=f"🌟 Наилучший объём", 
            callback_data="best_volume_params_0"
        )],
        [InlineKeyboardButton(
            text=f"🔧 Доп. параметры", 
            callback_data="additional_params_0"
        )],
        [InlineKeyboardButton(text="👀 Предпросмотр", callback_data="show_msg"),InlineKeyboardButton(text="⬅️ Назад", callback_data="msg_back")],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def category_params_keyboard(user: User, params_list: List[Tuple[int, str]], page: int = 0, category_key: str = "", all_enabled: bool = False) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с параметрами для конкретной категории с пагинацией"""
    # Настройки пагинации
    ITEMS_PER_PAGE = 6  # 3 строки по 2 параметра
    
    # Разбиваем параметры на страницы
    total_pages = (len(params_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_params = params_list[start_idx:end_idx]
    
    buttons = []
    
    # Кнопка включения/отключения всей категории
    toggle_text = "❌ Отключить всю категорию" if all_enabled else "✅ Включить всю категорию"
    # Добавляем суффикс _params если он отсутствует
    full_category_key = category_key if category_key.endswith("_params") else f"{category_key}_params"
    buttons.append([InlineKeyboardButton(
        text=toggle_text,
        callback_data=f"toggle_category_{full_category_key}"
    )])
    
    # Кнопки параметров - по 2 в строке
    param_buttons = []
    for i, (bit, name) in enumerate(current_params):
        is_enabled = user.is_param_enabled(bit)
        status = "✅" if is_enabled else "❌"
        
        # Создаем кнопку параметра
        # Добавляем суффикс _params если он отсутствует
        full_category_key = category_key if category_key.endswith("_params") else f"{category_key}_params"
        param_button = InlineKeyboardButton(
            text=f"{status} {name}",
            callback_data=f"toggle_category_param_{bit}_{page}_{full_category_key}"
        )
        
        # Добавляем в текущую строку или создаем новую
        if i % 2 == 0:
            param_buttons.append([param_button])
        else:
            param_buttons[-1].append(param_button)
    
    buttons.extend(param_buttons)
    
    # Кнопки пагинации (если нужно)
    if total_pages > 1:
        pagination_buttons = []
        
        if page > 0:
            pagination_buttons.append(InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{category_key}_{page-1}"
            ))
        
        pagination_buttons.append(InlineKeyboardButton(
            text=f"{page+1}/{total_pages}",
            callback_data="ignore"
        ))
        
        if page < total_pages - 1:
            pagination_buttons.append(InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"{category_key}_{page+1}"
            ))
        
        buttons.append(pagination_buttons)
    
    # Кнопки навигации
    buttons.append([])
    
    buttons.append([
        InlineKeyboardButton(
            text="👀 Предпросмотр",
            callback_data="show_msg"
        ),
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="edit_params"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_exchanges_keyboard(user: User, page: int = 0) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с биржами для указанной страницы"""
    start_idx = page * EXCHANGES_ITEMS_PER_PAGE
    end_idx = start_idx + EXCHANGES_ITEMS_PER_PAGE
    current_exchanges = EXCHANGES_LIST[start_idx:end_idx]
    
    buttons = []
    
    # Заголовок с кнопками Вывод/Депозит
    buttons.append([
        InlineKeyboardButton(text="Название", callback_data="___"),
        InlineKeyboardButton(text="Вывод", callback_data="___"),
        InlineKeyboardButton(text="Депозит", callback_data="___")
    ])
    
    # Кнопки бирж
    for bit, name in current_exchanges:
        withdraw_status = "✅" if user.is_withdraw_exchange_enabled(bit) else "❌"
        deposit_status = "✅" if user.is_deposit_exchange_enabled(bit) else "❌"
        
        buttons.append([
            InlineKeyboardButton(text=name, callback_data=f"exchange_info_{bit}"),
            InlineKeyboardButton(text=withdraw_status, callback_data=f"toggle_withdraw_{bit}_{page}"),
            InlineKeyboardButton(text=deposit_status, callback_data=f"toggle_deposit_{bit}_{page}")
        ])
    
    # Кнопки пагинации
    pagination_buttons = []
    total_pages = (len(EXCHANGES_LIST) + EXCHANGES_ITEMS_PER_PAGE - 1) // EXCHANGES_ITEMS_PER_PAGE
    
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"exchanges_page_{page-1}"
        ))
    
    pagination_buttons.append(InlineKeyboardButton(
        text=f"{page+1}/{total_pages}",
        callback_data="current_page"
    ))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"exchanges_page_{page+1}"
        ))
    
    if pagination_buttons:
        buttons.append(pagination_buttons)
    
    # Кнопка возврата
    buttons.append([InlineKeyboardButton(
        text="⬅️ Обратно в меню",
        callback_data="filters_back"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def edit_contract_keyboard(user: User) -> InlineKeyboardMarkup:
    status = "✅" if user.check_contract else "❌"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{status} Проверять контракты", callback_data="toggle_contract")],
        [InlineKeyboardButton(text="⬅️ Обратно в меню", callback_data="filters_back")]
    ])
