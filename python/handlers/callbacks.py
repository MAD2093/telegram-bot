from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from states.main import FilterStates, BlacklistStates
from database.models import User
from database.main import AsyncSessionLocal
from keyboards.main import *
from models.models import mock_server_data

from handlers.commands import send_grpc_update

callback_router = Router()

@callback_router.callback_query(F.data == "cancel_edit")
async def cb_cancel_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        def format_filter(min_val, max_val, suffix=""):
            if min_val > 0 and max_val > 0:
                if min_val == max_val:
                    return f"={min_val:.2f}{suffix}"
                else:
                    return f"{min_val:.2f} - {max_val:.2f}{suffix}"
            elif min_val > 0:
                return f"> {min_val:.2f}{suffix}"
            elif max_val > 0:
                return f"< {max_val:.2f}{suffix}"
            else:
                return "отключён"

        lines = [
            "⚙️ *Текущие фильтры:*\n",
            "❗ Фильтр неактивен, если его значение равно нулю\n",
            f"🔀 Спред: *{format_filter(user.spread_min, user.spread_max, ' %')}*",
            f"💰 Профит: *{format_filter(user.profit_min, user.profit_max, ' $')}*",
            f"📊 Объем: *{format_filter(user.volume_min, user.volume_max, ' $')}*",
            f"💸 Макс. комиссия: *{user.total_fee_max:.2f}$*" if user.total_fee_max > 0 else "💸 Макс. комиссия: *отключена*",
            f"📈 Мин. 24ч. оборот: *{user.daily_turnover_min:.2f}$*" if user.daily_turnover_min > 0 else "📈 Мин. 24ч. оборот: *отключён*",
            f"📃 Проверять контракты: *{'Да' if user.check_contract else 'Нет'}*"
        ]

        text = "\n".join(lines)
        await callback.message.edit_text(text, reply_markup=filters_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "cancel_freq")
async def cb_cancel_edit_freq(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await show_notifys(callback)

@callback_router.callback_query(F.data == "edit_spread")
async def cb_edit_spread(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎯 *Настройка диапазона спреда*\n\n"
        "Укажите минимальное и максимальное значение спреда в процентах.\n\n"
        "💡 *Доступные форматы:*\n"
        "• `1 5` - спреды от 1% до 5%\n"
        "• `0 3.5` - спреды до 3.5%\n" 
        "• `2 0` - спреды от 2%\n"
        "• `0 0` - отключить фильтр\n\n"
        "📝 *Формат ввода:* два числа через пробел\n"
        "✅ *Пример:* `1.5 5.0`",
        reply_markup=cancel_keyboard("edit"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.edit_spread)

@callback_router.callback_query(F.data == "edit_profit")
async def cb_edit_profit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 *Настройка диапазона профита*\n\n"
        "Укажите минимальную и максимальную прибыль в долларах.\n\n"
        "💡 *Доступные форматы:*\n"
        "• `10 50` - профит от $10 до $50\n"
        "• `0 25` - профит до $25\n"
        "• `15 0` - профит от $15\n"
        "• `0 0` - отключить фильтр\n\n"
        "📝 *Формат ввода:* два числа через пробел\n"
        "✅ *Пример:* `5.5 20.0`",
        reply_markup=cancel_keyboard("edit"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.edit_profit)

@callback_router.callback_query(F.data == "edit_volume")
async def cb_edit_volume(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📊 *Настройка диапазона объема*\n\n"
        "Укажите минимальный и максимальный объем в долларах.\n\n"
        "💡 *Доступные форматы:*\n"
        "• `1000 5000` - объем от $1000 до $5000\n"
        "• `0 2000` - объем до $2000\n"
        "• `500 0` - объем от $500\n"
        "• `0 0` - отключить фильтр\n\n"
        "📝 *Формат ввода:* два числа через пробел\n"
        "✅ *Пример:* `1500.50 3000.75`",
        reply_markup=cancel_keyboard("edit"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.edit_volume)

@callback_router.callback_query(F.data == "edit_fee")
async def cb_edit_fee(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💸 *Настройка максимальной комиссии*\n\n"
        "Укажите максимально допустимую комиссию в долларах.\n\n"
        "💡 *Доступные форматы:*\n"
        "• `5` - комиссия не более $5\n"
        "• `0` - отключить фильтр\n\n"
        "📝 *Формат ввода:* одно число\n"
        "✅ *Пример:* `3.75`",
        reply_markup=cancel_keyboard("edit"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.edit_fee)

@callback_router.callback_query(F.data == "edit_daily_turnover")
async def cb_daily_turnover(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📈 *Настройка минимального 24ч. оборота*\n\n"
        "Укажите минимальный суточный оборот в долларах.\n\n"
        "💡 *Доступные форматы:*\n"
        "• `10000` - оборот от $10,000\n"
        "• `0` - отключить фильтр\n\n"
        "📝 *Формат ввода:* одно число\n"
        "✅ *Пример:* `15000.75`",
        reply_markup=cancel_keyboard("edit"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.edit_daily_turnover)

@callback_router.callback_query(F.data == "edit_blacklists")
async def cb_edit_blacklists(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите, что хотите редактировать:", reply_markup=blacklist_keyboard())

@callback_router.callback_query(F.data == "edit_blacklist_coins")
async def cb_blacklist_coins(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        coins_list = user.blacklisted_coins or []
        
        if not coins_list:
            text = (
                "🚫 *Черный список монет*\n\n"
                "📝 Список пуст\n\n"
                "Добавьте монеты, которые хотите исключить из поиска"
            )
        else:
            # Группируем по 3 монеты в строку
            coins_chunks = [coins_list[i:i+3] for i in range(0, len(coins_list), 3)]
            coins_formatted = "\n".join([f"· {' | '.join(chunk)}" for chunk in coins_chunks])
            text = (
                "🚫 *Черный список монет*\n\n"
                f"{coins_formatted}\n\n"
                f"📋 Всего исключено: *{len(coins_list)}* монет"
            )

        await callback.message.edit_text(
            text, 
            reply_markup=coins_blacklist_keyboard(),
            parse_mode="Markdown"
        )

@callback_router.callback_query(F.data == "filters_back")
async def cb_filters_back(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        def format_filter(min_val, max_val, suffix=""):
            if min_val > 0 and max_val > 0:
                if min_val == max_val:
                    return f"={min_val:.2f}{suffix}"
                else:
                    return f"{min_val:.2f} - {max_val:.2f}{suffix}"
            elif min_val > 0:
                return f"> {min_val:.2f}{suffix}"
            elif max_val > 0:
                return f"< {max_val:.2f}{suffix}"
            else:
                return "отключён"

        lines = [
            "⚙️ *Текущие фильтры:*\n",
            "❗ Фильтр неактивен, если его значение равно нулю\n",
            f"🔀 Спред: *{format_filter(user.spread_min, user.spread_max, ' %')}*",
            f"💰 Профит: *{format_filter(user.profit_min, user.profit_max, ' $')}*",
            f"📊 Объем: *{format_filter(user.volume_min, user.volume_max, ' $')}*",
            f"💸 Макс. комиссия: *{user.total_fee_max:.2f}$*" if user.total_fee_max > 0 else "💸 Макс. комиссия: *отключена*",
            f"📈 Мин. 24ч. оборот: *{user.daily_turnover_min:.2f}$*" if user.daily_turnover_min > 0 else "📈 Мин. 24ч. оборот: *отключён*",
            f"📃 Проверять контракты: *{'Да' if user.check_contract else 'Нет'}*"
        ]

        text = "\n".join(lines)
        await callback.message.edit_text(text, reply_markup=filters_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "edit_blacklist_nets")
async def cb_blacklist_nets(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        nets_list = user.blacklisted_nets or []
        
        if not nets_list:
            text = (
                "🌐 *Черный список сетей*\n\n"
                "📝 Список пуст\n\n"
                "Добавьте сети, которые хотите исключить из поиска"
            )
        else:
            # группируем по 3 сети в строку
            nets_chunks = [nets_list[i:i+3] for i in range(0, len(nets_list), 3)]
            nets_formatted = "\n".join([f"· {' | '.join(chunk)}" for chunk in nets_chunks])
            text = (
                "🌐 *Черный список сетей*\n\n"
                f"{nets_formatted}\n\n"
                f"📊 Всего: {len(nets_list)} сетей"
            )

        await callback.message.edit_text(
            text, 
            reply_markup=nets_blacklist_keyboard(),
            parse_mode="Markdown"
        )

@callback_router.callback_query(F.data == "add_coin")
async def cb_add_coin(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        coins_list = user.blacklisted_coins or []
        
        if not coins_list:
            current_list = "📭 Список пуст"
        else:
            coins_chunks = [coins_list[i:i+3] for i in range(0, len(coins_list), 3)]
            current_list = "\n".join([f"· {' | '.join(chunk)}" for chunk in coins_chunks])

        await callback.message.edit_text(
            "🚫 *Добавление монет в ЧС*\n\n"
            f"📋 *Текущий список:*\n{current_list}\n\n"
            "💡 *Как добавить:*\n"
            "Введите названия монет через запятую\n\n"
            "✅ *Пример:*\n"
            "`BTC, ETH, USDT, SOL`\n\n"
            "⚡ Монеты будут исключены из поиска арбитражных пар",
            reply_markup=cancel_keyboard("edit"),
            parse_mode="Markdown"
        )
    await state.set_state(BlacklistStates.add_coin)

@callback_router.callback_query(F.data == "remove_coin")
async def cb_remove_coin(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        coins_list = user.blacklisted_coins or []
        
        if not coins_list:
            await callback.message.edit_text(
                "📭 *Черный список монет пуст*\n\n"
                "Нечего удалять! Сначала добавьте монеты в ЧС.",
                reply_markup=coins_blacklist_keyboard(),
                parse_mode="Markdown"
            )
            return

        coins_chunks = [coins_list[i:i+3] for i in range(0, len(coins_list), 3)]
        current_list = "\n".join([f"· {' | '.join(chunk)}" for chunk in coins_chunks])

        await callback.message.edit_text(
            "✅ *Удаление монет из ЧС*\n\n"
            f"📋 *Текущий список:*\n{current_list}\n\n"
            f"📊 Всего монет: {len(coins_list)}\n\n"
            "💡 *Как удалить:*\n"
            "Введите названия монет через запятую\n\n"
            "✅ *Пример:*\n"
            "`BTC, ETH, SOL`\n\n"
            "⚡ Эти монеты снова будут участвовать в поиске",
            reply_markup=cancel_keyboard("edit"),
            parse_mode="Markdown"
        )
    await state.set_state(BlacklistStates.remove_coin)

@callback_router.callback_query(F.data == "add_net")
async def cb_add_net(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        nets_list = user.blacklisted_nets or []
        
        if not nets_list:
            current_list = "📭 Список пуст"
        else:
            nets_chunks = [nets_list[i:i+3] for i in range(0, len(nets_list), 3)]
            current_list = "\n".join([f"· {' | '.join(chunk)}" for chunk in nets_chunks])

        await callback.message.edit_text(
            "🌐 *Добавление сетей в ЧС*\n\n"
            f"📋 *Текущий список:*\n{current_list}\n\n"
            "💡 *Как добавить:*\n"
            "Введите названия сетей через запятую\n\n"
            "✅ *Пример:*\n"
            "`Ethereum, BSC, Polygon`\n\n"
            "⚡ Сети будут исключены из поиска арбитражных пар",
            reply_markup=cancel_keyboard("edit"),
            parse_mode="Markdown"
        )
    await state.set_state(BlacklistStates.add_net)

@callback_router.callback_query(F.data == "remove_net")
async def cb_remove_net(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден. Используйте /start.")
            return

        nets_list = user.blacklisted_nets or []
        
        if not nets_list:
            await callback.message.edit_text(
                "📭 *Черный список сетей пуст*\n\n"
                "Нечего удалять! Сначала добавьте сети в ЧС.",
                reply_markup=nets_blacklist_keyboard(),
                parse_mode="Markdown"
            )
            return

        nets_chunks = [nets_list[i:i+3] for i in range(0, len(nets_list), 3)]
        current_list = "\n".join([f"· {' | '.join(chunk)}" for chunk in nets_chunks])

        await callback.message.edit_text(
            "✅ *Удаление сетей из ЧС*\n\n"
            f"📋 *Текущий список:*\n{current_list}\n\n"
            f"📊 Всего сетей: {len(nets_list)}\n\n"
            "💡 *Как удалить:*\n"
            "Введите названия сетей через запятую\n\n"
            "✅ *Пример:*\n"
            "`Ethereum, BSC`\n\n"
            "⚡ Эти сети снова будут участвовать в поиске",
            reply_markup=cancel_keyboard("edit"),
            parse_mode="Markdown"
        )
    await state.set_state(BlacklistStates.remove_net)

@callback_router.callback_query(F.data == "show_msg")
async def cb_show_msg(callback: types.CallbackQuery):
    mock_data = mock_server_data()
    
    # Расчет общей комиссии (аналогично Go версии)
    up_total_fee = mock_data.maker_fee * mock_data.data.up.ask_vol_usdt + mock_data.withdrawal_fee
    
    # Формирование сообщения
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Расчет общей комиссии
        up_total_fee = mock_data.maker_fee * mock_data.data.up.ask_vol_usdt + mock_data.withdrawal_fee
        low_total_fee = mock_data.maker_fee * mock_data.data.low.ask_vol_usdt + mock_data.withdrawal_fee
        
        # Формируем сообщение по частям
        message_parts = [
            f"<b>{mock_data.symbol} | {mock_data.withdrawal_exchange} → {mock_data.deposit_exchange} | "
            f"{mock_data.data.up.spread:.2f}% {mock_data.data.up.profit:.2f}$</b>\n\n",

            f"🪙 Монета: <b>{mock_data.symbol}</b>\n",
            f"🏦 Биржи: <b><a href=\"{mock_data.withdrawal_exchange_url}\">{mock_data.withdrawal_exchange}</a></b> → <b><a href=\"{mock_data.deposit_exchange_url}\">{mock_data.deposit_exchange}</a></b>\n",
            f"🔗 Сеть: <b>{mock_data.withdrawal_network}</b>\n\n",

            # Блок 1 – первая биржа (Ask)
            f"<b><a href=\"{mock_data.withdrawal_exchange_url}\">{mock_data.withdrawal_exchange}</a></b> | USDT → {mock_data.symbol}\n",
            f"    💰 Цена: <b>{mock_data.data.low.buy_price:.2f}$ - {mock_data.data.up.buy_price:.2f}$</b>\n",
            f"    📊 min. Объём:\n",
            f"        <b>{mock_data.data.low.ask_vol_usdt:.2f}</b> USDT\n",
            f"        <b>{mock_data.data.low.ask_vol_usdt / mock_data.data.low.buy_price:.2f}</b> {mock_data.symbol}\n",
            f"    📊 max. Объём:\n",
            f"        <b>{mock_data.data.up.ask_vol_usdt:.2f}</b> USDT\n",
            f"        <b>{mock_data.data.up.ask_vol_usdt / mock_data.data.up.buy_price:.2f}</b> {mock_data.symbol}\n\n",
            
            # Блок 2 – вторая биржа (Bid)
            f"<b><a href=\"{mock_data.deposit_exchange_url}\">{mock_data.deposit_exchange}</a></b> | {mock_data.symbol} → USDT\n",
            f"    💰 Цена: <b>{mock_data.data.low.sell_price:.2f}$ - {mock_data.data.up.sell_price:.2f}$</b>\n",
            f"    📊 min. Объём:\n",
            f"        <b>{mock_data.data.low.bid_vol_usdt}</b> USDT\n",
            f"        <b>{(mock_data.data.low.bid_vol_usdt) / mock_data.data.low.sell_price:.2f}</b> {mock_data.symbol}\n",
            f"    📊 max. Объём:\n",
            f"        <b>{mock_data.data.up.bid_vol_usdt}</b> USDT\n",
            f"        <b>{(mock_data.data.up.bid_vol_usdt) / mock_data.data.up.sell_price:.2f}</b> {mock_data.symbol}\n\n",
        ]
        
        # Блок max
        max_block = [f"<b>max. Объём:</b>"]
        if user.is_param_enabled(SPREAD_MAX_BIT):
            max_block.append(f"    🔀 Спред: <b>{mock_data.data.up.spread:.2f}%</b>")
        if user.is_param_enabled(PROFIT_MAX_BIT):
            max_block.append(f"    💵 Профит: <b>{mock_data.data.up.profit:.2f}$</b>")
        if user.is_param_enabled(COMMISSION_MAX_BIT):
            max_block.append(f"    ✂️ Комиссия: <b>{up_total_fee:.2f}$</b>")
        if max_block[1:]:
            message_parts.append("\n".join(max_block) + "\n")

        # Блок min
        min_block = [f"<b>min. Объём:</b>"]
        if user.is_param_enabled(SPREAD_MIN_BIT):
            min_block.append(f"    🔀 Спред: <b>{mock_data.data.low.spread:.2f}%</b>")
        if user.is_param_enabled(PROFIT_MIN_BIT):
            min_block.append(f"    💵 Профит: <b>{mock_data.data.low.profit:.2f}$</b>")
        if user.is_param_enabled(COMMISSION_MIN_BIT):
            min_block.append(f"    ✂️ Комиссия: <b>{low_total_fee:.2f}$</b>")
        if min_block[1:]:
            message_parts.append("\n".join(min_block) + "\n")

        message_parts.append("\n")

        # Остальные параметры
        if user.is_param_enabled(CHECK_CONTRACT_BIT):
            if mock_data.same_contracts:
                message_parts.append(f"✅ Контракты совпадают!\n")
            else:
                message_parts.append(f"❌ Контракты не совпадают!\n")
        if user.is_param_enabled(DAILY_TURNOVER_BIT):
            message_parts.append(f"🔄 24ч оборот: <b>{mock_data.volume24h}</b>\n")
        if user.is_param_enabled(WITHDRAW_TIME_BIT):
            message_parts.append(f"⏳ Время вывода: ~<b>{mock_data.withdrawal_time}</b>\n")
        if user.is_param_enabled(LIFETIME_BIT):
            message_parts.append(f"⏳ Время жизни: <b>{mock_data.time_life}</b>")

        # Убираем последний \n если он есть
        if message_parts and message_parts[-1].endswith('\n'):
            message_parts[-1] = message_parts[-1].rstrip('\n')
        
        message_text = ''.join(message_parts)

        await callback.message.edit_text(message_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=show_msg_keyboard())

@callback_router.callback_query(F.data == "msg_back")
async def msg_back(callback: types.CallbackQuery):
    text = (
        "🎨 *Персонализация уведомлений*\n\n"
        "Настройте содержание и внешний вид "
        "арбитражных пар. "
        "Выберите какие данные важны именно вам"
    )

    await callback.message.edit_text(text, reply_markup=msg_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "menu_msg")
async def show_msg(callback: types.CallbackQuery):
    text = (
        "🎨 *Персонализация уведомлений*\n\n"
        "Настройте содержание и внешний вид "
        "арбитражных пар. "
        "Выберите какие данные важны именно вам"
    )

    await callback.message.edit_text(text, reply_markup=msg_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "menu_settings")
async def show_settings(callback: types.CallbackQuery):
    text = (
        "⚙️ *Настройки бота*\n\n"
        "Здесь вы можете настроить параметры работы бота под свои потребности\n\n"
        "• *Фильтры* — настройка критериев для поиска арбитражных пар\n"
        "• *Настройка пары* — настройка текста арбитражной пары\n"
        "• *Частота уведомлений* — настройка частоты уведомлений о новых арбитражных возможностях"
    )

    await callback.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "edit_params")
async def cb_edit_params(callback: types.CallbackQuery):
    """Обработчик для редактирования параметров отображения"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        message_text = (
            "⚙️ <b>Настройка отображаемых параметров</b>\n\n"
            "Выберите категорию параметров для настройки:"
        )
        
        keyboard = main_params_keyboard()
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@callback_router.callback_query(F.data.startswith("max_volume_params"))
async def cb_max_volume_params(callback: types.CallbackQuery):
    """Обработчик для параметров макс объёма"""
    page = int(callback.data.split("_")[3]) if "_" in callback.data else 0
    await show_params_category(callback, "Максимальный объём", [
        (SPREAD_MAX_BIT, "Спред"),
        (PROFIT_MAX_BIT, "Профит"),
        (COMMISSION_MAX_BIT, "Комиссия"),
    ], page, "max_volume_params")

@callback_router.callback_query(F.data.startswith("min_volume_params"))
async def cb_min_volume_params(callback: types.CallbackQuery):
    """Обработчик для параметров мин объёма"""
    page = int(callback.data.split("_")[3]) if "_" in callback.data else 0
    await show_params_category(callback, "Минимальный объём", [
        (SPREAD_MIN_BIT, "Спред"),
        (PROFIT_MIN_BIT, "Профит"),
        (COMMISSION_MIN_BIT, "Комиссия"),
    ], page, "min_volume_params")

@callback_router.callback_query(F.data.startswith("best_volume_params"))
async def cb_best_volume_params(callback: types.CallbackQuery):
    """Обработчик для наилучшего объёма (заглушка)"""
    await callback.answer("Параметры для наилучшего объёма пока недоступны", show_alert=True)

@callback_router.callback_query(F.data.startswith("additional_params"))
async def cb_additional_params(callback: types.CallbackQuery):
    """Обработчик для дополнительных параметров"""
    page = int(callback.data.split("_")[2]) if "_" in callback.data else 0
    await show_params_category(callback, "Дополнительные параметры", [
        (CHECK_CONTRACT_BIT, "Проверка контрактов"),
        (DAILY_TURNOVER_BIT, "24ч оборот"),
        (WITHDRAW_TIME_BIT, "Время вывода"),
        (LIFETIME_BIT, "Время жизни"),
    ], page, "additional_params")

@callback_router.callback_query(F.data.startswith("toggle_category_param_"))
async def cb_toggle_category_param(callback: types.CallbackQuery):
    """Обработчик переключения параметра в категории"""
    parts = callback.data.split("_")
    bit = int(parts[3])
    page = int(parts[4])
    category_key = "_".join(parts[5:])  # соединяем все оставшиеся части для получения полного имени категории

    blacklisted_params = None
    
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Переключаем параметр
        user.toggle_param(bit)
        await session.commit()

        blacklisted_params = user.blacklisted_params
        
        # Определяем данные категории
        category_data = get_category_data(category_key)
        if category_data:
            category_name, params_list = category_data
            enabled_count = sum(1 for b, _ in params_list if user.is_param_enabled(b))
            all_enabled = enabled_count == len(params_list)
            
            message_text = (
                f"⚙️ <b>{category_name}</b>\n\n"
                "Нажмите на параметр, чтобы включить/выключить его отображение:"
            )
            
            keyboard = category_params_keyboard(user, params_list, page, category_key, all_enabled)
            await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        # Находим имя параметра
        param_name = next((name for b, name in PARAMETERS_LIST if b == bit), "Параметр")
        status = "включен" if user.is_param_enabled(bit) else "выключен"
        await callback.answer(f"{param_name} {status}")
    
    await send_grpc_update(callback.from_user.id, 'BlacklistedParams', blacklisted_params)

@callback_router.callback_query(F.data.startswith("toggle_category_"))
async def cb_toggle_category(callback: types.CallbackQuery):
    """Обработчик для включения/отключения всей категории"""
    # Получаем полное имя категории из callback_data
    parts = callback.data.split("_")
    category_key = "_".join(parts[2:])  # соединяем все оставшиеся части для получения полного имени категории
    all_enabled = False
    category_params = None
    user = None
    
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Определяем параметры категории
        category_params = get_category_params(category_key)  # Передаем category_key
        
        if category_params:
            # Проверяем, все ли параметры включены
            all_enabled = all(user.is_param_enabled(bit) for bit, _ in category_params)
            
            # Если все включены - отключаем все, иначе включаем все
            for bit, _ in category_params:
                if all_enabled:
                    user.disable_param(bit)
                else:
                    if not user.is_param_enabled(bit):
                        user.enable_param(bit)
            
            await session.commit()
        else:
            await callback.answer("Категория не найдена")
    # Обновляем клавиатуру
    keyboard = category_params_keyboard(user, category_params, 0, category_key, not all_enabled)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

    action = "отключена" if all_enabled else "включена"
    await callback.answer(f"Категория {action}")

    await send_grpc_update(callback.from_user.id, 'BlacklistedParams', user.blacklisted_params)

async def show_params_category(callback: types.CallbackQuery, category_name: str, params_list: List[Tuple[int, str]], page: int = 0, category_key: str = ""):
    """Показывает параметры для конкретной категории с пагинацией"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Подсчитываем активные параметры в этой категории
        enabled_count = sum(1 for bit, _ in params_list if user.is_param_enabled(bit))
        all_enabled = enabled_count == len(params_list)
        
        message_text = (
            f"⚙️ <b>{category_name}</b>\n\n"
            "Нажмите на параметр, чтобы включить/выключить его отображение:"
        )
        
        keyboard = category_params_keyboard(user, params_list, page, category_key, all_enabled)
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@callback_router.callback_query(F.data == "edit_exchanges")
async def cb_edit_exchanges(callback: types.CallbackQuery):
    """Обработчик для редактирования бирж"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Подсчитываем активные биржи
        enabled_withdraw = sum(1 for bit, _ in EXCHANGES_LIST if user.is_withdraw_exchange_enabled(bit))
        enabled_deposit = sum(1 for bit, _ in EXCHANGES_LIST if user.is_deposit_exchange_enabled(bit))
        
        message_text = (
            "🏦 <b>Настройка бирж</b>\n\n"
            f"Разрешено для вывода: <b>{enabled_withdraw}/{len(EXCHANGES_LIST)}</b>\n"
            f"Разрешено для депозита: <b>{enabled_deposit}/{len(EXCHANGES_LIST)}</b>\n\n"
            "Нажмите на ✅/❌ чтобы изменить статус биржи:\n"
            "• <b>✅ Вывод</b> - можно выводить с этой биржи\n"
            "• <b>✅ Депозит</b> - можно переводить на эту биржу"
        )
        
        keyboard = get_exchanges_keyboard(user, 0)
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@callback_router.callback_query(F.data.startswith("exchanges_page_"))
async def cb_exchanges_page(callback: types.CallbackQuery):
    """Обработчик переключения страниц бирж"""
    page = int(callback.data.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Подсчитываем активные биржи
        enabled_withdraw = sum(1 for bit, _ in EXCHANGES_LIST if user.is_withdraw_exchange_enabled(bit))
        enabled_deposit = sum(1 for bit, _ in EXCHANGES_LIST if user.is_deposit_exchange_enabled(bit))
        
        message_text = (
            "🏦 <b>Настройка бирж</b>\n\n"
            f"Разрешено для вывода: <b>{enabled_withdraw}/{len(EXCHANGES_LIST)}</b>\n"
            f"Разрешено для депозита: <b>{enabled_deposit}/{len(EXCHANGES_LIST)}</b>\n\n"
            "Нажмите на ✅/❌ чтобы изменить статус биржи:\n"
            "• <b>✅ Вывод</b> - можно выводить с этой биржи\n"
            "• <b>✅ Депозит</b> - можно переводить на эту биржу"
        )
        
        keyboard = get_exchanges_keyboard(user, page)
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@callback_router.callback_query(F.data.startswith("toggle_withdraw_"))
async def cb_toggle_withdraw(callback: types.CallbackQuery):
    """Обработчик переключения биржи для вывода"""
    parts = callback.data.split("_")
    bit = int(parts[2])
    page = int(parts[3])

    blacklisted_withdraw_exchanges = None
    
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Переключаем биржу для вывода
        user.toggle_withdraw_exchange(bit)
        await session.commit()

        blacklisted_withdraw_exchanges = user.blacklisted_withdraw_exchanges
        
        # Обновляем сообщение
        enabled_withdraw = sum(1 for b, _ in EXCHANGES_LIST if user.is_withdraw_exchange_enabled(b))
        enabled_deposit = sum(1 for b, _ in EXCHANGES_LIST if user.is_deposit_exchange_enabled(b))
        
        message_text = (
            "🏦 <b>Настройка бирж</b>\n\n"
            f"Разрешено для вывода: <b>{enabled_withdraw}/{len(EXCHANGES_LIST)}</b>\n"
            f"Разрешено для депозита: <b>{enabled_deposit}/{len(EXCHANGES_LIST)}</b>\n\n"
            "Нажмите на ✅/❌ чтобы изменить статус биржи:\n"
            "• <b>✅ Вывод</b> - можно выводить с этой биржи\n"
            "• <b>✅ Депозит</b> - можно переводить на эту биржу"
        )
        
        keyboard = get_exchanges_keyboard(user, page)
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        # Находим имя биржи
        exchange_name = next((name for b, name in EXCHANGES_LIST if b == bit), "Биржа")
        status = "разрешена" if user.is_withdraw_exchange_enabled(bit) else "заблокирована"
        await callback.answer(f"{exchange_name} {status} для вывода")
    await send_grpc_update(callback.from_user.id, 'BlacklistedWithdrawExchanges', blacklisted_withdraw_exchanges)

@callback_router.callback_query(F.data.startswith("toggle_deposit_"))
async def cb_toggle_deposit(callback: types.CallbackQuery):
    """Обработчик переключения биржи для депозита"""
    parts = callback.data.split("_")
    bit = int(parts[2])
    page = int(parts[3])
    
    blacklisted_deposit_exchanges = None

    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Переключаем биржу для депозита
        user.toggle_deposit_exchange(bit)
        await session.commit()
        blacklisted_deposit_exchanges = user.blacklisted_deposit_exchanges
        
        # Обновляем сообщение
        enabled_withdraw = sum(1 for b, _ in EXCHANGES_LIST if user.is_withdraw_exchange_enabled(b))
        enabled_deposit = sum(1 for b, _ in EXCHANGES_LIST if user.is_deposit_exchange_enabled(b))
        
        message_text = (
            "🏦 <b>Настройка бирж</b>\n\n"
            f"Разрешено для вывода: <b>{enabled_withdraw}/{len(EXCHANGES_LIST)}</b>\n"
            f"Разрешено для депозита: <b>{enabled_deposit}/{len(EXCHANGES_LIST)}</b>\n\n"
            "Нажмите на ✅/❌ чтобы изменить статус биржи:\n"
            "• <b>✅ Вывод</b> - можно выводить с этой биржи\n"
            "• <b>✅ Депозит</b> - можно переводить на эту биржу"
        )

        keyboard = get_exchanges_keyboard(user, page)
        await callback.message.edit_text(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        # Находим имя биржи
        exchange_name = next((name for b, name in EXCHANGES_LIST if b == bit), "Биржа")
        status = "разрешена" if user.is_deposit_exchange_enabled(bit) else "заблокирована"
        await callback.answer(f"{exchange_name} {status} для депозита")
    await send_grpc_update(callback.from_user.id, 'BlacklistedDepositExchanges', blacklisted_deposit_exchanges)

@callback_router.callback_query(F.data.startswith("edit_contract"))
async def cb_edit_contract(callback: types.CallbackQuery):
    """Обработчик для редактирования фильтра по контрактам"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        status = "включен" if user.check_contract else "выключен"
        message_text = (
            "📃 <b>Фильтр по контрактам</b>\n\n"
            f"Текущий статус: <b>{status}</b>\n\n"
            "Если фильтр включен - будут попадаться только пары, прошедшие проверку контрактов в сети блокчейна.\n\n"
            "❗ На данный момент, не все биржи имеют адрес контракта монеты\n"
            "❗ Биржи для хэджинга не проходят проверку контрактов\n\n"
            "Нажмите кнопку ниже, чтобы переключить состояние фильтра."
        )

        await callback.message.edit_text(message_text, reply_markup=edit_contract_keyboard(user), parse_mode="HTML")
        await callback.answer()

@callback_router.callback_query(F.data == "toggle_contract")
async def cb_toggle_contract(callback: types.CallbackQuery):
    """Обработчик переключения фильтра по контрактам"""
    check_contract = None
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        # Переключаем фильтр
        user.check_contract = not user.check_contract
        await session.commit()

        check_contract = user.check_contract
        
        # Обновляем сообщение
        status = "включен" if user.check_contract else "выключен"
        message_text = (
            "📃 <b>Фильтр по контрактам</b>\n\n"
            f"Текущий статус: <b>{status}</b>\n\n"
            "Если фильтр включен - будут попадаться только пары, прошедшие проверку контрактов в сети блокчейна.\n\n"
            "❗ На данный момент, не все биржи имеют адрес контракта монеты\n"
            "❗ Биржи для хэджинга не проходят проверку контрактов\n\n"
            "Нажмите кнопку ниже, чтобы переключить состояние фильтра."
        )
        
        await callback.message.edit_text(message_text, reply_markup=edit_contract_keyboard(user), parse_mode="HTML")
        await callback.answer(f"Фильтр по контрактам {status}")
    await send_grpc_update(callback.from_user.id, 'CheckContract', check_contract)

@callback_router.callback_query(F.data == "menu_notifys")
async def show_notifys(callback: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Форматируем текущее значение для отображения
        total_seconds = user.notification_frequency or 0
        time_display = 0
        
        # Форматируем время для отображения
        if total_seconds < 60:
            time_display = f"{total_seconds} секунд" + ("у" if total_seconds == 1 else ("ы" if 2 <= total_seconds <= 4 else ""))
        elif total_seconds < 3600:  # меньше часа
            minutes_total = total_seconds // 60
            remaining_seconds = total_seconds % 60
            
            if remaining_seconds == 0:
                time_display = f"{minutes_total} минут" + ("у" if minutes_total == 1 else ("ы" if 2 <= minutes_total <= 4 else ""))
            else:
                minutes_text = f"{minutes_total} минут" + ("у" if minutes_total == 1 else ("ы" if 2 <= minutes_total <= 4 else ""))
                seconds_text = f"{remaining_seconds} секунд" + ("у" if remaining_seconds == 1 else ("ы" if 2 <= remaining_seconds <= 4 else ""))
                time_display = f"{minutes_text} {seconds_text}"
        else:
            hours_total = total_seconds // 3600
            remaining_minutes = (total_seconds % 3600) // 60
            remaining_seconds = total_seconds % 60
            
            if remaining_minutes == 0 and remaining_seconds == 0:
                time_display = f"{hours_total} час" + ("а" if 2 <= hours_total <= 4 else "ов" if hours_total >= 5 else "")
            elif remaining_seconds == 0:
                hours_text = f"{hours_total} час" + ("а" if 2 <= hours_total <= 4 else "ов" if hours_total >= 5 else "")
                minutes_text = f"{remaining_minutes} минут" + ("у" if remaining_minutes == 1 else ("ы" if 2 <= remaining_minutes <= 4 else ""))
                time_display = f"{hours_text} {minutes_text}"
            else:
                hours_text = f"{hours_total} час" + ("а" if 2 <= hours_total <= 4 else "ов" if hours_total >= 5 else "")
                minutes_text = f"{remaining_minutes} минут" + ("у" if remaining_minutes == 1 else ("ы" if 2 <= remaining_minutes <= 4 else ""))
                seconds_text = f"{remaining_seconds} секунд" + ("у" if remaining_seconds == 1 else ("ы" if 2 <= remaining_seconds <= 4 else ""))
                time_display = f"{hours_text} {minutes_text} {seconds_text}"

        text = (
            "🔄 *Настройка частоты уведомлений*\n\n"
            "📊 *Текущая настройка:*\n"
            f"Раз в {time_display}\n\n"
            "Здесь вы можете настроить то, как часто будут приходить "
            "уведомления об одной и той же арбитражной паре.\n\n"
            "❓ *Зачем это нужно*\n"
            "Чтобы не спамить парами при каждом их обновлении\n"
            "Пара обновляется до актуальных значений несколько раз в минуту\n\n"
            "Выберите подходящий интервал:"
        )

        await callback.message.edit_text(text, reply_markup=notifys_keyboard(), parse_mode="Markdown")

@callback_router.callback_query(F.data == "freq_instant")
async def cb_freq_instant(callback: types.CallbackQuery):
    """Обработчик - при каждом обновлении"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        user.notification_frequency = -1
        await session.commit()
        await send_grpc_update(callback.from_user.id, 'NotificationFrequency', -1)
        
        await callback.message.edit_text(
            "✅ *Настройки обновлены!*\n\n"
            "🔔 Теперь вы будете получать уведомления "
            "*при каждом обновлении* арбитражной пары",
            reply_markup=notifys_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()

@callback_router.callback_query(F.data == "freq_15min")
async def cb_freq_15min(callback: types.CallbackQuery):
    """Обработчик - раз в 15 минут"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        user.notification_frequency = 15 * 60
        await session.commit()
        await send_grpc_update(callback.from_user.id, 'NotificationFrequency', 15 * 60)
        
        await callback.message.edit_text(
            "✅ *Настройки обновлены!*\n\n"
            "⏰ Теперь вы будете получать уведомления "
            "*не чаще чем раз в 15 минут*",
            reply_markup=notifys_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()

@callback_router.callback_query(F.data == "freq_1hour")
async def cb_freq_1hour(callback: types.CallbackQuery):
    """Обработчик - раз в час"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        user.notification_frequency = 3600
        await session.commit()
        await send_grpc_update(callback.from_user.id, 'NotificationFrequency', 3600)
        
        await callback.message.edit_text(
            "✅ *Настройки обновлены!*\n\n"
            "🕐 Теперь вы будете получать уведомления "
            "*не чаще чем раз в час*",
            reply_markup=notifys_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()

@callback_router.callback_query(F.data == "freq_custom")
async def cb_freq_custom(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик - своё значение"""
    await callback.message.edit_text(
        "⚙️ *Настройка своего интервала*\n\n"
        "Введите интервал в формате:\n"
        "`1h10m5s` - 1 час 10 минут 5 секунд\n\n"
        "💡 *Примеры:*\n"
        "• `30m` - 30 минут\n"
        "• `2h` - 2 часа\n"
        "• `1h30m` - 1 час 30 минут\n"
        "• `15m30s` - 15 минут 30 секунд\n"
        "• `2h15m10s` - 2 часа 15 минут 10 секунд\n\n"
        "📝 *Формат:* часы(h) минуты(m) секунды(s)",
        reply_markup=cancel_keyboard("freq"),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.custom_frequency)
    await callback.answer()

@callback_router.callback_query(F.data == "freq_never")
async def cb_freq_never(callback: types.CallbackQuery):
    """Обработчик - отключить повторы"""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        user.notification_frequency = 0
        await session.commit()
        await send_grpc_update(callback.from_user.id, 'NotificationFrequency', 0)
        
        await callback.message.edit_text(
            "✅ *Настройки обновлены!*\n\n"
            "🚫 **Повторные уведомления отключены**\n\n"
            "💡 Вы будете получать уведомление только "
            "при первом появлении арбитражной пары",
            reply_markup=notifys_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()
