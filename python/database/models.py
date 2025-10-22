from sqlalchemy import Column, Integer, Boolean, Float, BigInteger, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    tg_id = Column(BigInteger, primary_key=True)
    active = Column(Boolean, default=False)

    spread_min = Column(Float, default=0.0)
    spread_max = Column(Float, default=0.0)

    profit_min = Column(Float, default=0.0)
    profit_max = Column(Float, default=0.0)
    
    volume_min = Column(Float, default=0.0)
    volume_max = Column(Float, default=0.0)
    
    total_fee_max = Column(Float, default=0.0)
    daily_turnover_min = Column(Float, default=0.0)

    check_contract = Column(Boolean, default=True)

    notification_frequency = Column(SmallInteger, default=900)
    
    blacklisted_deposit_exchanges = Column(Integer, default=0)  # uint32 stored as INTEGER
    blacklisted_withdraw_exchanges = Column(Integer, default=0)  # uint32 stored as INTEGER
    blacklisted_coins = Column(JSONB, default=list)
    blacklisted_nets = Column(JSONB, default=list)
    blacklisted_params = Column(Integer, default=0)  # uint32 stored as INTEGER

    def is_param_enabled(self, bit: int) -> bool:
        """Проверяет, активен ли параметр (бит не установлен в черном списке)"""
        return (self.blacklisted_params & bit) == 0

    def toggle_param(self, bit: int):
        """Переключает состояние параметра"""
        self.blacklisted_params ^= bit
    
    def enable_param(self, bit: int):
        """Включает параметр (убирает бит из черного списка)"""
        self.blacklisted_params &= ~bit
    
    def disable_param(self, bit: int):
        """Отключает параметр (устанавливает бит в черный список)"""
        self.blacklisted_params |= bit

    def is_deposit_exchange_enabled(self, exchange_bit: int) -> bool:
        """Проверяет, разрешена ли биржа для депозита (бит не установлен в черном списке)"""
        return (self.blacklisted_deposit_exchanges & exchange_bit) == 0
    
    def toggle_deposit_exchange(self, exchange_bit: int):
        """Переключает состояние биржи для депозита"""
        self.blacklisted_deposit_exchanges ^= exchange_bit
    
    def is_withdraw_exchange_enabled(self, exchange_bit: int) -> bool:
        """Проверяет, разрешена ли биржа для вывода (бит не установлен в черном списке)"""
        return (self.blacklisted_withdraw_exchanges & exchange_bit) == 0
    
    def toggle_withdraw_exchange(self, exchange_bit: int):
        """Переключает состояние биржи для вывода"""
        self.blacklisted_withdraw_exchanges ^= exchange_bit
