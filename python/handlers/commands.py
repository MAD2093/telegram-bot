from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.main import AsyncSessionLocal
from config.main import GRPC_PORT, GRPC_ADDR
import asyncio
import json
import logging
from typing import Any, Union

from database.models import User
from keyboards.main import filters_keyboard, settings_keyboard, msg_keyboard

logger = logging.getLogger(__name__)
router = Router()


async def send_grpc_update(tg_id: int, filter_name: str, data: Union[str, Any]) -> dict:
    """
    Асинхронно отправляет обновление фильтров через gRPC
    
    Args:
        tg_id: Telegram ID пользователя
        filter_name: Название фильтра
        data: Данные для обновления (автоматически конвертируется в JSON если не строка)
    
    Returns:
        dict: Результат операции
    """
    from clients.grpc_client import FilterSyncClient as _Client
    
    # Подготавливаем данные
    if not isinstance(data, str):
        payload = json.dumps(data)
    else:
        payload = data
    
    logger.info(f"Sending gRPC update: user_id={tg_id}, filter={filter_name}")
    
    def _call() -> dict:
        """Синхронный вызов в отдельном потоке"""
        client = None
        try:
            target = f"{GRPC_ADDR}:{GRPC_PORT}"
            logger.debug(f"Connecting to gRPC server at {target}")
            
            client = _Client(target=target)
            
            # Теперь метод всегда возвращает dict, даже при ошибках
            result = client.update_user_filters(
                tg_id=tg_id, 
                filter=filter_name,
                data=payload
            )
            
            # Логируем результат
            if result.get('success'):
                logger.info(f"gRPC update successful: user_id={tg_id}, filter={filter_name}, msg={result.get('message')}")
            else:
                logger.warning(f"gRPC update failed: user_id={tg_id}, filter={filter_name}, error={result.get('message')}")
            
            return result
            
        except Exception as e:
            logger.error(f"gRPC client initialization error: user_id={tg_id}, filter={filter_name}, error={str(e)}")
            return {
                'success': False,
                'message': f'gRPC client initialization error: {str(e)}'
            }
        finally:
            if client:
                try:
                    client.close()
                except Exception as e:
                    logger.debug(f"gRPC client close error: {e}")
    
    # Запускаем в отдельном потоке
    return await asyncio.to_thread(_call)


# Интерактивный туториал для новых пользователей
TUTORIAL_STEPS = [
    (
        "🎯 *Добро пожаловать в MAD Scanner!*\n\n"
        "MAD Scanner — это профессиональный инструмент для поиска арбитражных возможностей.\n\n"
        "Бот помогает находить прибыльные торговые возможности между 17-и криптобирж "
        "в режиме реального времени.\n\n"
        "🚀 Ознакомьтесь с основными функциями!"
    ),
    (
        "⚙️ *Инструменты фильтрации*\n\n"
        "Доступные параметры для поиска арбитражных возможностей:\n"
        "• *Спред* (%) — разница в ценах между биржами\n"
        "• *Профит* ($) — чистая прибыль с учетом комиссий\n"
        "• *Ликвидность* — 24-часовой оборот пары\n"
        "• *Безопасность* — проверка смарт-контрактов\n"
        "• *Черные списки* — защита от нежелательных активов\n\n"
        "_И много других параметров для точной настройки поиска_\n\n"
        "📍 Команда /filters или через\n"
        "/settings → *Фильтры*"
    ),
    (
        "🔔 *Настройка уведомлений*\n\n"
        "Контролируйте поток информации об арбитражных возможностях:\n"
        "• Выбор интервала между уведомлениями\n"
        "• Возможность приостановки уведомлений\n\n"
        "Это поможет вам сфокусироваться на действительно важных сигналах "
        "и не пропустить выгодные возможности.\n\n"
        "📍 Настройка через\n"
        "/settings → *Частота уведомлений*"
    ),
    (
        "🎨 *Персонализация уведомлений*\n\n"
        "Настройте формат отображения арбитражных пар под свои потребности\n"
        "Сделайте интерфейс максимально удобным и информативным для вашего "
        "стиля торговли.\n\n"
        "📍 Команда /msg или через\n"
        "/settings → *Настройка пары*"
    ),
    (
        "✨ *Всё готово к работе!*\n\n"
        "Основные команды:\n\n"
        "• /settings — все настройки бота\n"
        "• /filters — настройка параметров поиска\n"
        "• /msg — персонализация уведомлений\n\n"
        "Успешного арбитража! 📈"
    ),
]

@router.message(Command("tutorial"))
async def tutorial_cmd(message: types.Message, state: FSMContext, command: CommandObject = None):
    # Начинаем туториал с первого шага
    await state.update_data(tutorial_step=0)
    builder = InlineKeyboardBuilder()
    builder.button(text="Далее", callback_data="tutorial_next")
    await message.answer(TUTORIAL_STEPS[0], reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(lambda c: c.data == "tutorial_next")
async def tutorial_next_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get("tutorial_step", 0) + 1
    if step < len(TUTORIAL_STEPS) - 1:
        builder = InlineKeyboardBuilder()
        builder.button(text="Далее", callback_data="tutorial_next")
        await callback.message.edit_text(TUTORIAL_STEPS[step], reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.update_data(tutorial_step=step)
    elif step == len(TUTORIAL_STEPS) - 1:
        builder = InlineKeyboardBuilder()
        builder.button(text="Завершить", callback_data="tutorial_finish")
        await callback.message.edit_text(TUTORIAL_STEPS[step], reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.update_data(tutorial_step=step)
    else:
        await callback.answer("Туториал уже завершён.", show_alert=True)


@router.callback_query(lambda c: c.data == "tutorial_finish")
async def tutorial_finish_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await settings_cmd(callback.message)


@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, message.from_user.id)
            if not user:
                user = User(
                    tg_id=message.from_user.id,
                    active=True,
                )
                session.add(user)

                await session.commit()

                # Запуск туториала для новых пользователей
                await state.update_data(tutorial_step=0)

                builder = InlineKeyboardBuilder()
                builder.button(text="Далее", callback_data="tutorial_next")
                await message.answer(TUTORIAL_STEPS[0], reply_markup=builder.as_markup(), parse_mode="Markdown")
            else:
                await message.answer(
                    "С возвращением!\n"
                    "Используйте /settings для настройки сканера."
                )
    # регистрация user в Golang-серисе с помощью gRPC
    await send_grpc_update(message.from_user.id, 'NewUser', '')


@router.message(Command("settings"))
async def settings_cmd(message: types.Message):
    text = (
        "⚙️ *Настройки бота*\n\n"
        "Здесь вы можете настроить параметры работы бота под свои потребности\n\n"
        "• *Фильтры* — настройка критериев для поиска арбитражных пар\n"
        "• *Настройка пары* — настройка текста арбитражной пары\n"
        "• *Частота уведомлений* — настройка частоты уведомлений о новых арбитражных возможностях"
    )

    await message.answer(text, reply_markup=settings_keyboard(), parse_mode="Markdown")


@router.message(Command("filters"))
async def filters_cmd(message: types.Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Пользователь не найден. Используйте /start.")
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
        await message.answer(text, reply_markup=filters_keyboard(), parse_mode="Markdown")


@router.message(Command("msg"))
async def msg_cmd(message: types.Message):
    text = (
        "🎨 *Персонализация уведомлений*\n\n"
        "Настройте содержание и внешний вид "
        "арбитражных пар. "
        "Выберите какие данные важны именно вам"
    )

    await message.answer(text, reply_markup=msg_keyboard(), parse_mode="Markdown")
