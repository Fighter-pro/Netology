# Домашнее задание «Aiohttp»

REST API для сайта объявлений на `aiohttp`.

## Реализовано

- `POST /advertisements` — создать объявление
- `GET /advertisements` — получить список объявлений
- `GET /advertisements/{id}` — получить объявление
- `PATCH /advertisements/{id}` — изменить объявление
- `DELETE /advertisements/{id}` — удалить объявление
- асинхронное хранение данных через `aiosqlite`
- валидация обязательных полей при создании и редактировании

Поля объявления:

- заголовок
- описание
- дата создания
- владелец

## Запуск локально

```bash
python -m venv venv
pip install -r requirements.txt
python server.py
```

API доступно на `http://127.0.0.1:8080`.

## Docker

Собрать образ:

```bash
docker build -t aiohttp-homework .
```

Запустить контейнер:

```bash
docker run --rm -p 8080:8080 aiohttp-homework
```

После запуска API доступно на `http://127.0.0.1:8080`.
