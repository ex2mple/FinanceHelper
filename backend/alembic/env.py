import asyncio
from logging.config import fileConfig

# Импортируем асинхронные компоненты SQLAlchemy
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine # Импортируем create_async_engine

from alembic import context

# Ваш импорт настроек
from core.config import settings
# !!! ВАЖНО: Импортируйте Base или metadata из ваших моделей SQLAlchemy !!!
try:
    from core.models.base import Base # <<<=== ЗАМЕНИТЕ ЭТУ СТРОКУ НА ПРАВИЛЬНЫЙ ИМПОРТ
    target_metadata = Base.metadata
except ImportError:
    print("=" * 80)
    print("!!! ОШИБКА: Не удалось импортировать метаданные моделей SQLAlchemy.")
    print("!!! Пожалуйста, исправьте импорт 'from models.base import Base' в alembic/env.py")
    print("!!! на правильный путь к вашему Base или объекту metadata.")
    print("=" * 80)
    target_metadata = None # Оставляем None, чтобы скрипт не упал полностью, но autogenerate не сработает

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем URL из ваших настроек
# Заменяет значение из alembic.ini, если оно там есть
# create_async_engine будет использовать это значение
db_url_for_alembic = settings.DB_URL_ALEMBIC
print(f"--- Alembic использует DB URL: {db_url_for_alembic} ---")
config.set_main_option("sqlalchemy.url", db_url_for_alembic)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Используем URL, который мы установили выше
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Рекомендуется для autogenerate
        compare_server_default=True, # Рекомендуется для autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()

# Вспомогательная синхронная функция для запуска миграций
def do_run_migrations(connection):
    """Выполняет настройку контекста и запуск миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Рекомендуется для autogenerate
        compare_server_default=True, # Рекомендуется для autogenerate
        # include_schemas=True, # Раскомментируйте, если используете схемы Postgres
    )

    # Выполняем миграции внутри транзакции
    with context.begin_transaction():
        context.run_migrations()


# ИЗМЕНЕНО: Функция стала асинхронной
async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Создаем АСИНХРОННЫЙ движок напрямую из URL настроек
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"), # Получаем URL, который установили ранее
        poolclass=pool.NullPool, # NullPool рекомендуется для миграций
        # echo=True, # Можно раскомментировать для отладки SQL-запросов
    )

    # Используем АСИНХРОННОЕ соединение
    async with connectable.connect() as connection:
        # Выполняем синхронную функцию do_run_migrations через run_sync
        # Это создает необходимый greenlet контекст
        await connection.run_sync(do_run_migrations)

    # Освобождаем ресурсы движка (важно для NullPool)
    await connectable.dispose()


# Основной блок выполнения
if context.is_offline_mode():
    print("Запуск миграций в offline режиме...")
    run_migrations_offline()
else:
    print("Запуск миграций в online режиме...")
    # ИЗМЕНЕНО: Запускаем асинхронную функцию через asyncio.run()
    asyncio.run(run_migrations_online())

print("--- Завершение env.py ---")