# src/server.py
import logging

import fastapi
from fastapi import Query, HTTPException
from pydantic import BaseModel
from src.preprocess import CATEGORY_NAMES
from src.model_train import Model
from src.preprocess import MAX_CATEGORY_INDEX

app = fastapi.FastAPI()

model = None


@app.on_event("startup")
async def startup_event():
    global model
    print("Инициализация моделей...")
    model = Model()
    model.load()
    print(model.models)

    if not model.models:
        print("Не удалось загрузить все модели. Производится обучение...")
        model.create()

        model.train(30)
        model.save("model")
        print("Обучение завершено, модели сохранены!")
    else:
        print("Нейросети успешно загружены!")


class OverspendingResponse(BaseModel):
    overspending_categories: dict


@app.get("/overspending", response_model=OverspendingResponse)
def get_overspending(
        age: int = Query(..., ge=14, le=80, description="Возраст пользователя"),
        gender: str = Query(..., regex="^[MFmf]$", description="Пол пользователя (M или F)"),
        income: float = Query(..., ge=0, le=3000, description="Ежемесячный доход"),
        expense_other: float = Query(default=0, description="Фактические траты для категории other"),
        expense_supermarkets: float = Query(default=0, description="Фактические траты для категории supermarkets"),
        expense_restaurants: float = Query(default=0, description="Фактические траты для категории restaurants"),
        expense_junk_food: float = Query(default=0, description="Фактические траты для категории junk_food"),
        expense_beauty: float = Query(default=0, description="Фактические траты для категории beauty"),
        expense_cosmetics: float = Query(default=0, description="Фактические траты для категории cosmetics"),
        expense_home_repair: float = Query(default=0, description="Фактические траты для категории home_repair"),
        expense_electronics: float = Query(default=0, description="Фактические траты для категории electronics"),
        expense_auto_services: float = Query(default=0, description="Фактические траты для категории auto_services"),
        expense_flowers: float = Query(default=0, description="Фактические траты для категории flowers"),
        expense_pets: float = Query(default=0, description="Фактические траты для категории pets"),
        expense_clothing: float = Query(default=0, description="Фактические траты для категории clothing"),
        expense_transport: float = Query(default=0, description="Фактические траты для категории transport"),
        expense_local_transport: float = Query(default=0,
                                               description="Фактические траты для категории local transport"),
        expense_train: float = Query(default=0, description="Фактические траты для категории train"),
        expense_airplane: float = Query(default=0, description="Фактические траты для категории airplane"),
        expense_taxi: float = Query(default=0, description="Фактические траты для категории taxi"),
        expense_medicine: float = Query(default=0, description="Фактические траты для категории medicine"),
        expense_digital_goods: float = Query(default=0, description="Фактические траты для категории digital_goods"),
        expense_entertainment: float = Query(default=0, description="Фактические траты для категории entertainment"),
        expense_cinema: float = Query(default=0, description="Фактические траты для категории cinema"),
        expense_online_cinema: float = Query(default=0, description="Фактические траты для категории online_cinema"),
        expense_stationery: float = Query(default=0, description="Фактические траты для категории stationery"),
        expense_travel: float = Query(default=0, description="Фактические траты для категории travel"),
        expense_hotels: float = Query(default=0, description="Фактические траты для категории hotels"),
        expense_souvenirs: float = Query(default=0, description="Фактические траты для категории souvenirs"),
        expense_fuel: float = Query(default=0, description="Фактические траты для категории fuel"),
        expense_pharmacies: float = Query(default=0, description="Фактические траты для категории pharmacies"),
        expense_sports_goods: float = Query(default=0, description="Фактические траты для категории sports_goods"),
        expense_children_goods: float = Query(default=0, description="Фактические траты для категории children_goods"),
        expense_books: float = Query(default=0, description="Фактические траты для категории books"),
        expense_education: float = Query(default=0, description="Фактические траты для категории education"),
        expense_car_rental: float = Query(default=0, description="Фактические траты для категории car_rental"),
        expense_utilities: float = Query(default=0, description="Фактические траты для категории utilities"),
        expense_marketplaces: float = Query(default=0, description="Фактические траты для категории marketplaces"),
        expense_gambling: float = Query(default=0, description="Фактические траты для категории gambling")
):
    if model is None:
        raise HTTPException(status_code=503, detail="Модель ещё не инициализирована")

    gender_numeric = 1 if gender.upper() == "M" else 0
    input_data = [[gender_numeric, age, income]]
    predicted_expenses = model.predict(input_data)[0]

    actual_expenses = [
        expense_other,
        expense_supermarkets,
        expense_restaurants,
        expense_junk_food,
        expense_beauty,
        expense_cosmetics,
        expense_home_repair,
        expense_electronics,
        expense_auto_services,
        expense_flowers,
        expense_pets,
        expense_clothing,
        expense_transport,
        expense_local_transport,
        expense_train,
        expense_airplane,
        expense_taxi,
        expense_medicine,
        expense_digital_goods,
        expense_entertainment,
        expense_cinema,
        expense_online_cinema,
        expense_stationery,
        expense_travel,
        expense_hotels,
        expense_souvenirs,
        expense_fuel,
        expense_pharmacies,
        expense_sports_goods,
        expense_children_goods,
        expense_books,
        expense_education,
        expense_car_rental,
        expense_utilities,
        expense_marketplaces,
        expense_gambling
    ]

    overspending = {}
    for idx, category in CATEGORY_NAMES.items():
        diff = actual_expenses[idx] - predicted_expenses[idx]
        print(f"{category} -> Реальные траты: {actual_expenses[idx]}, Ожидаемые траты: {predicted_expenses[idx]}")
        if diff > 0:
            overspending[category] = (int(float(actual_expenses[idx])), int(float(predicted_expenses[idx])))

    return {"overspending_categories": overspending}
