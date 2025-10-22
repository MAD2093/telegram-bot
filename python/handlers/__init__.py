from .commands import router
from .state import register_handlers

# Регистрируем обработчики состояний на router
register_handlers(router)
