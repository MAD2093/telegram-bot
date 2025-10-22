import json
import re
import asyncio
import logging

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage

from database.main import AsyncSessionLocal
from database.models import User
from handlers.commands import filters_cmd, send_grpc_update, settings_cmd
from states.main import FilterStates, BlacklistStates
from config.main import REDIS_ADDR, REDIS_PASSWORD

logger = logging.getLogger(__name__)


# Redis setup for storage
host, port = REDIS_ADDR.split(":")
redis_url = f"redis://:{REDIS_PASSWORD}@{host}:{port}" if REDIS_PASSWORD else f"redis://{host}:{port}"
storage = RedisStorage.from_url(redis_url)

async def process_add_coin(message: types.Message, state: FSMContext):
    coins_input = message.text.strip().upper()
    coins_to_add = [c.strip() for c in coins_input.split(",") if c.strip()]
    if not coins_to_add:
        await message.answer("❌ Не указаны монеты.\nВведите названия монет для добавления в ЧС, через запятую.")
        return
    updated_coins = []

    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден. Используйте /start.")
                await state.clear()
                return

            current_coins = set(user.blacklisted_coins or [])
            already_blacklisted = [c for c in coins_to_add if c in current_coins]
            new_coins = [c for c in coins_to_add if c not in current_coins]

            if not new_coins:
                await message.answer("❌ Все указанные монеты уже в ЧС: " + "; ".join(already_blacklisted))
                await filters_cmd(message)
            else:
                updated_coins = list(current_coins.union(new_coins))
                user.blacklisted_coins = updated_coins
                await session.commit()

                msg = f"✅ Монеты добавленные в ЧС:\n{'; '.join(new_coins)}"
                if already_blacklisted:
                    msg += f"\n\n❌ Уже были в ЧС:\n{'; '.join(already_blacklisted)}"
                await message.answer(msg)
                await filters_cmd(message)
    await send_grpc_update(message.from_user.id, 'BlacklistedCoins', updated_coins)
    await state.clear()

async def process_remove_coin(message: types.Message, state: FSMContext):
    coins_input = message.text.strip().upper()
    coins_to_remove = [c.strip() for c in coins_input.split(",") if c.strip()]
    if not coins_to_remove:
        await message.answer("❌ Не указаны монеты.\nВведите названия монет для удаления из ЧС, через запятую.")
        return

    blacklisted_coins = []

    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден. Используйте /start.")
                await state.clear()
                return

            current_coins = set(user.blacklisted_coins or [])
            not_in_blacklist = [c for c in coins_to_remove if c not in current_coins]
            coins_to_remove_actual = [c for c in coins_to_remove if c in current_coins]

            if not coins_to_remove_actual:
                await message.answer("❌ Ни одной из указанных монет нет в ЧС: " + "; ".join(not_in_blacklist))
                await filters_cmd(message)
            else:
                user.blacklisted_coins = [c for c in current_coins if c not in coins_to_remove_actual]
                await session.commit()

                blacklisted_coins = user.blacklisted_coins

                msg = f"✅ Монеты удалённые из ЧС:\n{'; '.join(coins_to_remove_actual)}"
                if not_in_blacklist:
                    msg += f"\n\n❌ Не были в ЧС:\n{'; '.join(not_in_blacklist)}"
                await message.answer(msg)
                await filters_cmd(message)
    await send_grpc_update(message.from_user.id, 'BlacklistedCoins', blacklisted_coins)
    await state.clear()

async def process_add_net(message: types.Message, state: FSMContext):
    nets_input = message.text.strip().upper()
    nets_to_add = [n.strip() for n in nets_input.split(",") if n.strip()]
    if not nets_to_add:
        await message.answer("❌ Не указаны сети.\nВведите названия сетей для добавления в ЧС, через запятую.")
        return
    
    updated_nets = []

    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден. Используйте /start.")
                await state.clear()
                return

            current_nets = set(user.blacklisted_nets or [])
            already_blacklisted = [n for n in nets_to_add if n in current_nets]
            new_nets = [n for n in nets_to_add if n not in current_nets]

            if not new_nets:
                await message.answer("❌ Все указанные сети уже в ЧС: " + "; ".join(already_blacklisted))
                await filters_cmd(message)
            else:
                updated_nets = list(current_nets.union(new_nets))
                user.blacklisted_nets = updated_nets
                await session.commit()

                msg = f"✅ Сети добавленные в ЧС:\n{'; '.join(new_nets)}"
                if already_blacklisted:
                    msg += f"\n\n❌ Уже были в ЧС:\n{'; '.join(already_blacklisted)}"
                await message.answer(msg)
                await filters_cmd(message)
    await send_grpc_update(message.from_user.id, 'BlacklistedNets', updated_nets)
    await state.clear()

async def process_remove_net(message: types.Message, state: FSMContext):
    nets_input = message.text.strip().upper()
    nets_to_remove = [n.strip() for n in nets_input.split(",") if n.strip()]
    if not nets_to_remove:
        await message.answer("❌ Не указаны сети.\nВведите названия сетей для удаления из ЧС, через запятую.")
        return

    blacklisted_nets = []

    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден. Используйте /start.")
                await state.clear()
                return

            current_nets = set(user.blacklisted_nets or [])
            not_in_blacklist = [n for n in nets_to_remove if n not in current_nets]
            nets_to_remove_actual = [n for n in nets_to_remove if n in current_nets]

            if not nets_to_remove_actual:
                await message.answer("❌ Ни одной из указанных сетей нет в ЧС: " + "; ".join(not_in_blacklist))
                await filters_cmd(message)
            else:
                user.blacklisted_nets = [n for n in current_nets if n not in nets_to_remove_actual]
                await session.commit()

                blacklisted_nets = user.blacklisted_nets

                msg = f"✅ Сети удалённые из ЧС:\n{'; '.join(nets_to_remove_actual)}"
                if not_in_blacklist:
                    msg += f"\n\n❌ Не были в ЧС:\n{'; '.join(not_in_blacklist)}"
                await message.answer(msg)
                await filters_cmd(message)
    await send_grpc_update(message.from_user.id, 'BlacklistedNets', blacklisted_nets)
    await state.clear()

async def process_spread(message: types.Message, state: FSMContext):
    try:
        parts = message.text.replace(",", ".").split()
        if len(parts) != 2:
            await message.answer("❌ Формат: <мин> <макс>\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        min_spread, max_spread = float(parts[0]), float(parts[1])
        if min_spread < 0 or max_spread < 0:
            await message.answer("❌ Значения не могут быть отрицательными.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_spread != 0 and min_spread > max_spread:
            await message.answer("❌ Минимальный спред должен быть меньше максимального (или 0 для отключения)\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_spread > 0 and min_spread > 0 and min_spread == max_spread:
            await message.answer("❌ Минимальный и максимальный спред не могут быть равны при ненулевых значениях.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user = await session.get(User, message.from_user.id)
                user.spread_min = min_spread
                user.spread_max = max_spread
                await session.commit()
        if min_spread == 0 and max_spread == 0:
            await message.answer("✅ Фильтр по спреду отключён.")
        else:
            await message.answer(f"✅ Спред обновлен: {min_spread:.2f} - {max_spread:.2f} %")
        await state.clear()
        await filters_cmd(message)
        await send_grpc_update(message.from_user.id, 'SpreadMin', min_spread)
        await send_grpc_update(message.from_user.id, 'SpreadMax', max_spread)
    except ValueError:
        await message.answer("❌ Некорректные значения.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")

async def process_volume(message: types.Message, state: FSMContext):
    try:
        parts = message.text.replace(",", ".").split()
        if len(parts) != 2:
            await message.answer("❌ Формат: <мин> <макс>\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        min_vol, max_vol = float(parts[0]), float(parts[1])
        if min_vol < 0 or max_vol < 0:
            await message.answer("❌ Значения не могут быть отрицательными.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_vol != 0 and min_vol > max_vol:
            await message.answer("❌ Минимальный объем должен быть меньше максимального (или 0 для отключения)\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_vol > 0 and min_vol > 0 and min_vol == max_vol:
            await message.answer("❌ Минимальный и максимальный объем не могут быть равны при ненулевых значениях.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user = await session.get(User, message.from_user.id)
                user.volume_min = min_vol
                user.volume_max = max_vol
                await session.commit()
        if min_vol == 0 and max_vol == 0:
            await message.answer("✅ Фильтр по объёму отключён.")
        else:
            await message.answer(f"✅ Объем обновлен: {min_vol:.2f} - {max_vol:.2f} $")
        await state.clear()
        await filters_cmd(message)
        await send_grpc_update(message.from_user.id, 'VolumeMin', min_vol)
        await send_grpc_update(message.from_user.id, 'VolumeMax', max_vol)
    except ValueError:
        await message.answer("❌ Некорректные значения. Введите ещё раз или нажмите кнопку отмены, или введите команду /start.")

async def process_fee(message: types.Message, state: FSMContext):
    try:
        fee = float(message.text.replace(",", "."))
        if fee < 0:
            await message.answer("❌ Значение не может быть отрицательным.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user = await session.get(User, message.from_user.id)
                user.total_fee_max = fee
                await session.commit()
        if fee == 0:
            await message.answer("✅ Фильтр по комиссии отключён.")
        else:
            await message.answer(f"✅ Максимальная комиссия обновлена: {fee:.2f} $")
        await state.clear()
        await filters_cmd(message)
        await send_grpc_update(message.from_user.id, 'TotalFeeMax', fee)
    except ValueError:
        await message.answer("❌ Некорректное значение.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")

async def process_daily_turnover(message: types.Message, state: FSMContext):
    try:
        daily_turnover = float(message.text.replace(",", "."))
        if daily_turnover < 0:
            await message.answer("❌ Значение не может быть отрицательным.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user = await session.get(User, message.from_user.id)
                user.daily_turnover_min = daily_turnover
                await session.commit()
        if daily_turnover == 0:
            await message.answer("✅ Фильтр по 24ч. обороту отключён.")
        else:
            await message.answer(f"✅ Минимальный 24ч. оборот обновлён: {daily_turnover:.2f} $")
        await state.clear()
        await filters_cmd(message)
        await send_grpc_update(message.from_user.id, 'DailyTurnoverMin', daily_turnover)
    except ValueError:
        await message.answer("❌ Некорректное значение.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")

async def process_profit(message: types.Message, state: FSMContext):
    try:
        parts = message.text.replace(",", ".").split()
        if len(parts) != 2:
            await message.answer("❌ Формат: <мин> <макс>\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        min_profit, max_profit = float(parts[0]), float(parts[1])
        if min_profit < 0 or max_profit < 0:
            await message.answer("❌ Значения не могут быть отрицательными.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_profit != 0 and min_profit > max_profit:
            await message.answer("❌ Минимальный профит должен быть меньше максимального (или 0 для отключения)\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        if max_profit > 0 and min_profit > 0 and min_profit == max_profit:
            await message.answer("❌ Минимальный и максимальный профит не могут быть равны при ненулевых значениях.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")
            return
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user = await session.get(User, message.from_user.id)
                user.profit_min = min_profit
                user.profit_max = max_profit
                await session.commit()
        if min_profit == 0 and max_profit == 0:
            await message.answer("✅ Фильтр по профиту отключён.")
        else:
            await message.answer(f"✅ Профит обновлен: {min_profit:.2f} - {max_profit:.2f} $")
        await state.clear()
        await filters_cmd(message)
        await send_grpc_update(message.from_user.id, 'ProfitMin', min_profit)
        await send_grpc_update(message.from_user.id, 'ProfitMax', max_profit)
    except ValueError:
        await message.answer("❌ Некорректные значения.\nВведите ещё раз или нажмите кнопку отмены, или введите команду /start.")

async def process_custom_frequency(message: types.Message, state: FSMContext):
    try:
        input_text = message.text.strip().lower()
        
        if not re.match(r'^(\d+h)?(\d+m)?(\d+s)?$', input_text):
            await message.answer(
                "❌ Неверный формат. Используйте например: `1h30m`\n"
                "Допустимые форматы: 1h, 30m, 1h30m, 15m30s, 2h15m10s\n"
                "Попробуйте еще раз:",
                parse_mode="Markdown"
            )
            return
        
        hours = int(re.search(r'(\d+)h', input_text).group(1)) if 'h' in input_text else 0
        minutes = int(re.search(r'(\d+)m', input_text).group(1)) if 'm' in input_text else 0
        seconds = int(re.search(r'(\d+)s', input_text).group(1)) if 's' in input_text else 0
        
        if hours < 0 or minutes < 0 or seconds < 0:
            await message.answer("❌ Значения не могут быть отрицательными\nПопробуйте еще раз:")
            return
        
        # Конвертируем всё в секунды
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        if total_seconds <= 0:
            await message.answer("❌ Интервал должен быть больше 0\nПопробуйте еще раз:")
            return
        
        async with AsyncSessionLocal() as session:
            user = await session.get(User, message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден")
                return
            
            user.notification_frequency = total_seconds
            await session.commit()
        
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
        
        await message.answer(
            f"✅ *Настройки обновлены!*\n\n"
            f"Теперь вы будете получать уведомления:\n"
            f"Не чаще чем раз в {time_display}\n\n",
            parse_mode="Markdown"
        )
        await state.clear()
        await settings_cmd(message)
        await send_grpc_update(message.from_user.id, 'NotificationFrequency', total_seconds)        
    except (ValueError, AttributeError):
        await message.answer(
            "❌ Неверный формат. Используйте например: `1h30m`\n"
            "Попробуйте еще раз:",
            parse_mode="Markdown"
        )

def register_handlers(router: Router):
    router.message.register(process_add_coin, BlacklistStates.add_coin)
    router.message.register(process_remove_coin, BlacklistStates.remove_coin)
    router.message.register(process_add_net, BlacklistStates.add_net)
    router.message.register(process_remove_net, BlacklistStates.remove_net)

    router.message.register(process_spread, FilterStates.edit_spread)
    router.message.register(process_profit, FilterStates.edit_profit)
    router.message.register(process_volume, FilterStates.edit_volume)
    router.message.register(process_fee, FilterStates.edit_fee)
    router.message.register(process_daily_turnover, FilterStates.edit_daily_turnover)
    router.message.register(process_custom_frequency, FilterStates.custom_frequency)
