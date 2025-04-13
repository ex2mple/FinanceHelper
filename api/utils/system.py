import random
import string
import colorsys

from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.security import get_password_hash
from api.users.crud import get_user_by_id
from core.models import User, Category


default_categories = ['Супермаркеты', 'Рестораны', 'Фастфуд', 'Красота', 'Косметика', 'Дом и ремонт',
                          'Электроника и техника', 'Автоуслуги', 'Цветы', 'Животные', 'Одежда и обувь', 'Транспорт',
                          'Местный транспорт', 'Ж/д билеты', 'Авиабилеты', 'Такси', 'Медицина', 'Цифровые товары',
                          'Развлечения', 'Кино', 'Онлайн-кинотеатры', 'Канцтовары', 'Турагентства', 'Отели', 'Сувениры',
                          'Топливо', 'Аптеки', 'Спорттовары', 'Детские товары', 'Книги', 'Образование', 'Аренда авто',
                          'Каршеринг', 'ЖКХ', 'Маркетплейсы', 'Азартные игры и лотереи']


CATEGORY_NAMES = {
    0: 'other',
    1: 'supermarkets',
    2: 'restaurants',
    3: 'junk_food',
    4: 'beauty',
    5: 'cosmetics',
    6: 'home_repair',
    7: 'electronics',
    8: 'auto_services',
    9: 'flowers',
    10: 'pets',
    11: 'clothing',
    12: 'transport',
    13: "local_transport",
    14: 'train',
    15: 'airplane',
    16: 'taxi',
    17: 'medicine',
    18: 'digital_goods',
    19: 'entertainment',
    20: 'cinema',
    21: 'online_cinema',
    22: 'stationery',
    23: 'travel',
    24: 'hotels',
    25: 'souvenirs',
    26: 'fuel',
    27: 'pharmacies',
    28: 'sports_goods',
    29: 'children_goods',
    30: 'books',
    31: 'education',
    32: 'car_rental',
    33: 'utilities',
    34: 'marketplaces',
    35: 'gambling',
}


def convert_category_to_numeric(category: str) -> int:
    categories = {
        'Супермаркеты': 1,
        'Рестораны': 2,
        'Фастфуд': 3,
        'Красота': 4,
        'Косметика': 5,
        'Дом и ремонт': 6,
        'Электроника и техника': 7,
        'Автоуслуги': 8,
        'Цветы': 9,
        'Животные': 10,
        'Одежда и обувь': 11,
        'Транспорт': 12,
        'Местный транспорт': 13,
        'Ж/д билеты': 14,
        'Авиабилеты': 15,
        'Такси': 16,
        'Медицина': 17,
        'Цифровые товары': 18,
        'Развлечения': 19,
        'Кино': 20,
        'Онлайн-кинотеатры': 21,
        'Канцтовары': 22,
        'Турагентства': 23,
        'Отели': 24,
        'Сувениры': 25,
        'Топливо': 26,
        'Аптеки': 27,
        'Спорттовары': 28,
        'Детские товары': 29,
        'Книги': 30,
        'Образование': 31,
        'Аренда авто': 32,
        'Каршеринг': 32,
        'ЖКХ': 33,
        'Маркетплейсы': 34,
        'Азартные игры и лотереи': 35,
    }

    if category in categories:
        return categories[category]
    return 0


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
    exists_system_user = await get_user_by_id(session, -1)
    if exists_system_user:
        return

    s = string.digits + string.ascii_uppercase + string.ascii_lowercase
    user = User(
        id=-1,
        username='System',
        password=get_password_hash("".join(random.choices(s, k=16))),
        gender='Male',
        age=0,
        salary=0,
        email='system@system.com'
    )
    session.add(user)
    await session.commit()
    await session.refresh(user, ["transactions", "advices", "categories"])
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
        await session.refresh(new_cat, ["transactions", "user"])
    print('Дефолтные категории созданы.')
