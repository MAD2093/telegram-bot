from typing import List, Tuple

# Константы для битовой маски
SPREAD_MAX_BIT = 1 << 0  # (бит 0: max. спред)
SPREAD_MIN_BIT = 1 << 1  # (бит 1: min. спред)

PROFIT_MAX_BIT = 1 << 2  # (бит 2: max. профит)
PROFIT_MIN_BIT = 1 << 3  # (бит 3: min. профит)

COMMISSION_MAX_BIT = 1 << 4  # (бит 4: max. комиссия)
COMMISSION_MIN_BIT = 1 << 5  # (бит 5: min. комиссия)

WITHDRAW_TIME_BIT = 1 << 6  # (бит 6: время вывода)
LIFETIME_BIT = 1 << 7       # (бит 7: время жизни)
CHECK_CONTRACT_BIT = 1 << 8 # (бит 8: нужна ли проверка контрактов)
DAILY_TURNOVER_BIT = 1 << 9 # (бит 9: 24ч оборот)


# Список всех параметров для отображения
PARAMETERS_LIST: List[Tuple[int, str]] = [
    (SPREAD_MAX_BIT, "Спред"),
    (SPREAD_MIN_BIT, "Спред"),
    (PROFIT_MAX_BIT, "Профит"),
    (PROFIT_MIN_BIT, "Профит"),
    (COMMISSION_MAX_BIT, "Комиссия"),
    (COMMISSION_MIN_BIT, "Комиссия"),
    (CHECK_CONTRACT_BIT, "Проверка контрактов"),
    (DAILY_TURNOVER_BIT, "24ч оборот"),
    (WITHDRAW_TIME_BIT, "Время вывода"),
    (LIFETIME_BIT, "Время жизни"),
]
PARAMETERS_ITEMS_PER_PAGE = 4


# Константы для битовой маски
EXCHANGE_BINANCE_BIT = 1 << 0
EXCHANGE_KUCOIN_BIT = 1 << 1
EXCHANGE_MEXC_BIT = 1 << 2
EXCHANGE_BYBIT_BIT = 1 << 3
EXCHANGE_GATE_BIT = 1 << 4
EXCHANGE_OKX_BIT = 1 << 5
EXCHANGE_BITGET_BIT = 1 << 6
EXCHANGE_BINGX_BIT = 1 << 7
EXCHANGE_HTX_BIT = 1 << 8
EXCHANGE_POLONIEX_BIT = 1 << 9
EXCHANGE_BITMART_BIT = 1 << 10
EXCHANGE_COINEX_BIT = 1 << 11
EXCHANGE_COINW_BIT = 1 << 12
EXCHANGE_XT_BIT = 1 << 13
EXCHANGE_ASCENDEX_BIT = 1 << 14
EXCHANGE_BITRUE_BIT = 1 << 15
EXCHANGE_DIGIFINEX_BIT = 1 << 16

# Список всех бирж для отображения
EXCHANGES_LIST: List[Tuple[int, str]] = [
    (EXCHANGE_BINANCE_BIT, "Binance"),
    (EXCHANGE_KUCOIN_BIT, "Kucoin"),
    (EXCHANGE_MEXC_BIT, "Mexc"),
    (EXCHANGE_BYBIT_BIT, "Bybit"),
    (EXCHANGE_GATE_BIT, "Gate"),
    (EXCHANGE_OKX_BIT, "OKX"),
    (EXCHANGE_BITGET_BIT, "Bitget"),
    (EXCHANGE_BINGX_BIT, "Bingx"),
    (EXCHANGE_HTX_BIT, "Htx"),
    (EXCHANGE_POLONIEX_BIT, "Poloniex"),
    (EXCHANGE_BITMART_BIT, "Bitmart"),
    (EXCHANGE_COINEX_BIT, "Coinex"),
    (EXCHANGE_COINW_BIT, "Coinw"),
    (EXCHANGE_XT_BIT, "Xt"),
    (EXCHANGE_ASCENDEX_BIT, "Ascendex"),
    (EXCHANGE_BITRUE_BIT, "Bitrue"),
    (EXCHANGE_DIGIFINEX_BIT, "Digifinex"),
]

EXCHANGES_ITEMS_PER_PAGE = 6
