import pandas as pd

MAX_CATEGORY_INDEX = 35

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


def preprocess_data(
        transactions_data_path: str = "../data/all_user_transactions.csv",
        users_data_path: str = "../data/users_data.csv",
):
    print("Preprocessing data...")
    transactions = pd.read_csv(transactions_data_path, sep=';')
    users = pd.read_csv(users_data_path, sep=';')

    users['gender'] = (users['gender_cd'] == 'M').astype(int)

    data = {}

    size = len(transactions)
    print(size)

    for i in range(size):
        if i % 100_000 == 0:
            print(f"Processed {i} transactions. Current progress: {i / size:.2%}")

        transaction = transactions.iloc[i]
        user_id = transaction['party_rk']
        category = convert_category_to_numeric(transaction['loyalty_cashback_category_nm'])
        amount = transaction['transaction_amt_rur']
        transaction_type = transaction['transaction_type_cd']

        if transaction_type != "PUC":
            continue

        if int(float(amount.replace(',', '.'))) > 100_000:
            if category in [23, 8, 6] and int(float(amount.replace(',', '.'))) < 250_000:
                continue
            print(f"{i}, user ID: {user_id}, amount: {amount}, category: {CATEGORY_NAMES[category]}, transaction_type: {transaction_type}")
            continue

        if user_id not in data:
            data[user_id] = [0] * (MAX_CATEGORY_INDEX + 1)

        data[user_id][category] += int(float(amount.replace(',', '.')))

    size = len(users)
    for i in range(size):
        user = users.iloc[i]
        user_id = user['party_rk']
        try:
            user_data = data[user_id]
        except KeyError:
            print(f"User {user_id} not found in transactions.")
            user_data = [0] * (MAX_CATEGORY_INDEX + 1)

        for j in range(MAX_CATEGORY_INDEX + 1):
            column_name = CATEGORY_NAMES.get(j, CATEGORY_NAMES[j])
            users.at[i, column_name] = user_data[j]

    spending_columns = list(CATEGORY_NAMES.values())
    users = users[(users[spending_columns] <= 200_000).all(axis=1)]
    users = users[(users['monthly_income_amt'] <= 2500) & (users['age'] <= 80)]

    users.to_csv('../data/users_processed.csv', index=False, sep=',')


if __name__ == "__main__":
    preprocess_data()
