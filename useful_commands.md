## Запуск контейнеров
```
docker-compose up --build -d
```
### Остановка контейнеров
```
docker-compose down
```

## Создание ревизии alembic
```
docker-compose exec app alembic revision --autogenerate -m "название ревизии"
```
### Применение ревизии

```
docker-compose exec app alembic upgrade head
```

