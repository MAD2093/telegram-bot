import random
from dataclasses import dataclass
from typing import List

# Определяем структуры данных
@dataclass
class Order:
    price: float
    amount: float

@dataclass
class OrderBook:
    asks: List[Order]
    bids: List[Order]

@dataclass
class UpperLimit:
    ask_vol_usdt: float
    bid_vol_usdt: float
    buy_price: float
    sell_price: float
    profit: float
    ask_depth: int
    bid_depth: int
    spread: float

@dataclass
class LowerLimit:
    ask_vol_usdt: float
    bid_vol_usdt: float
    buy_price: float
    sell_price: float
    profit: float
    ask_depth: int
    bid_depth: int
    spread: float

@dataclass
class VolumeData:
    up: UpperLimit
    low: LowerLimit

@dataclass
class ServerData:
    symbol: str
    deposit_exchange: str
    deposit_exchange_url: str
    withdrawal_exchange: str
    withdrawal_exchange_url: str
    withdrawal_network: str
    withdrawal_fee: float
    withdrawal_time: str
    maker_fee: float
    time_life: str
    data: VolumeData
    order_book: OrderBook
    volume24h: float
    same_contracts: bool

def mock_server_data() -> ServerData:
    """Генерация правдоподобных тестовых данных"""
    return ServerData(
        symbol="BTC",
        deposit_exchange="Kucoin",  # Исправлено с "KUCOIN" на "Kucoin"
        deposit_exchange_url="https://www.kucoin.com/trade/BTC-USDT",
        withdrawal_exchange="Mexc",  # Исправлено с "MEXC" на "Mexc"
        withdrawal_exchange_url="https://www.mexc.com/ru-RU/exchange/BTC_USDT",
        withdrawal_network="ERC20",
        withdrawal_fee=0.1,
        withdrawal_time=f"{random.randint(10, 59)}s",
        maker_fee=random.random() * 0.1 + 0.01,
        time_life=f"{random.randint(10, 59)}m",
        volume24h=142561,
        same_contracts=True,
        data=VolumeData(
            up=UpperLimit(
                ask_vol_usdt=3890,
                bid_vol_usdt=3894.511764705882,  # Исправлено с 3906
                buy_price=114.41176470588235,
                sell_price=114.88235294117646,
                profit=4.5117647058818875,
                ask_depth=4,
                bid_depth=5,
                spread=0.4113110539845744,
            ),
            low=LowerLimit(
                ask_vol_usdt=220,
                bid_vol_usdt=228,  # Исправлено с 240
                buy_price=110,
                sell_price=120,
                profit=8,
                ask_depth=1,
                bid_depth=1,
                spread=9.090909090909092,
            ),
        ),
        order_book=OrderBook(
            asks=[
                Order(110, 10),
                Order(115, 5),
                Order(116, 8),
                Order(117, 11),
                Order(120, 20),
            ],
            bids=[
                Order(120, 13),
                Order(115, 8),
                Order(113, 2),
                Order(111, 4),
                Order(108, 16),
            ],
        ),
    )