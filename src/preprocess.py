import pandas as pd

MAX_CATEGORY_INDEX = 25

CATEGORY_NAMES = {
    0: 'other',
    1: 'supermarkets',
    2: 'restaurants',
    3: 'beauty',
    4: 'home_repair',
    5: 'electronics',
    6: 'auto_services',
    7: 'flowers',
    8: 'pets',
    9: 'clothing',
    10: 'transport',
    11: 'medicine',
    12: 'digital_goods',
    13: 'entertainment',
    14: 'stationery',
    15: 'travel',
    16: 'fuel',
    17: 'pharmacies',
    18: 'sports_goods',
    19: 'children_goods',
    20: 'books',
    21: 'education',
    22: 'car_rental',
    23: 'utilities',
    24: 'marketplaces',
    25: 'gambling',
}


def convert_category_to_numeric(category: str) -> int:
    categories = {
        'Супермаркеты': 1,
        'Рестораны': 2,
        'Фастфуд': 2,
        'Красота': 3,
        'Косметика': 3,
        'Дом и ремонт': 4,
        'Электроника и техника': 5,
        'Автоуслуги': 6,
        'Цветы': 7,
        'Животные': 8,
        'Одежда и обувь': 9,
        'Транспорт': 10,
        'Местный транспорт': 10,
        'Ж/д билеты': 10,
        'Авиабилеты': 10,
        'Такси': 10,
        'Медицина': 11,
        'Цифровые товары': 12,
        'Развлечения': 13,
        'Кино': 13,
        'Онлайн-кинотеатры': 13,
        'Канцтовары': 14,
        'Турагентства': 15,
        'Отели': 15,
        'Сувениры': 15,
        'Топливо': 16,
        'Аптеки': 17,
        'Спорттовары': 18,
        'Детские товары': 19,
        'Книги': 20,
        'Образование': 21,
        'Аренда авто': 22,
        'Каршеринг': 22,
        'ЖКХ': 23,
        'Маркетплейсы': 24,
        'Азартные игры и лотереи': 25,
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
            if category in [15, 4, 6] and int(float(amount.replace(',', '.'))) < 250_000:
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
