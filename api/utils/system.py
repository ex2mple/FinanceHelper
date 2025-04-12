import random
import string
import colorsys

from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.security import get_password_hash
from api.users.crud import get_user_by_id
from core.models import User, Category


def generate_beautiful_color() -> str:
    """Генерирует красивый HEX-цвет с насыщенными значениями"""
    # Используем HSL модель для лучшего контроля над цветами
    # Случайный оттенок (hue) для разнообразия цветов
    h = random.random()  # от 0 до 1

    # Высокая насыщенность (saturation) для ярких цветов
    s = random.uniform(0.6, 0.9)  # от 0.6 до 0.9

    # Средняя яркость (lightness) для баланса между тёмными и светлыми
    l = random.uniform(0.4, 0.6)  # от 0.4 до 0.6

    # Конвертируем HSL в RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # Масштабируем до диапазона 0-255 и преобразуем в HEX
    hex_color = "#{:02x}{:02x}{:02x}".format(
        int(r * 255), int(g * 255), int(b * 255)
    )

    return hex_color


async def create_system_user_and_categories(session: AsyncSession) -> None:
    exists_system_user = get_user_by_id(session, -1)
    if exists_system_user:
        return

    s = string.digits + string.ascii_uppercase + string.ascii_lowercase
    user = User(
        username='System',
        password=get_password_hash("".join(random.choices(s, k=16))),
        gender='Male',
        age=0,
        salary=0,
        email='system@system.com'
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print('Системный юзер создан.')

    default_categories = ['Супермаркеты', 'Рестораны', 'Фастфуд', 'Красота', 'Косметика', 'Дом и ремонт',
                          'Электроника и техника', 'Автоуслуги', 'Цветы', 'Животные', 'Одежда и обувь', 'Транспорт',
                          'Местный транспорт', 'Ж/д билеты', 'Авиабилеты', 'Такси', 'Медицина', 'Цифровые товары',
                          'Развлечения', 'Кино', 'Онлайн-кинотеатры', 'Канцтовары', 'Турагентства', 'Отели', 'Сувениры',
                          'Топливо', 'Аптеки', 'Спорттовары', 'Детские товары', 'Книги', 'Образование', 'Аренда авто',
                          'Каршеринг', 'ЖКХ', 'Маркетплейсы', 'Азартные игры и лотереи']
    for cat in default_categories:
        new_cat = Category(user_id=user.id, name=cat,
                           color=generate_beautiful_color())
        session.add(new_cat)
    await session.commit()
    print('Дефолтные категории созданы.')
