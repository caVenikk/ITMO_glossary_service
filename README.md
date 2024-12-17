# Сервис Глоссария на FastAPI

REST API сервис для управления глоссарием, построенный на FastAPI, SQLAlchemy и SQLite.

## Реализованные требования

### Основные функции

- Получение списка всех терминов с поддержкой пагинации и поиска
- Получение информации о конкретном термине
- Добавление нового термина с описанием
- Обновление существующего термина
- Удаление термина из глоссария

### Дополнительные требования

- Автоматическая генерация документации через OpenAPI
- Контейнеризация с использованием Docker и Docker Compose
- Хранение данных в SQLite
- Автоматическая миграция структуры данных при старте

## Технологический стек

- FastAPI - веб-фреймворк
- SQLAlchemy 2.0 - ORM для работы с базой данных
- Alembic - система миграций
- SQLite - база данных
- Docker & Docker Compose - контейнеризация
- Pydantic - валидация данных
- Ruff - линтер и форматтер кода
- mypy - статическая типизация
- pre-commit - автоматизация проверок кода

## API Endpoints

- `GET /api/glossary` - Получение списка терминов
- `GET /api/glossary/{id}` - Получение конкретного термина
- `GET /api/glossary/search` - Поиск терминов
- `POST /api/glossary` - Создание нового термина
- `PUT /api/glossary/{id}` - Обновление термина
- `DELETE /api/glossary/{id}` - Удаление термина

## Структура проекта

```text
src/
├── database/
│   ├── alembic/         # Миграции базы данных
│   ├── fixtures/        # Начальные данные
│   ├── models/          # Модели SQLAlchemy
│   └── repositories/    # Работа с базой данных
├── exceptions/          # Ошибки приложения
├── routes/              # Маршруты API
├── schemas/             # Модели Pydantic
├── validators/          # Валидация входных данных
├── main.py              # Точка входа приложения
└── run.py               # Точка входа для запуска приложения
```

## Запуск проекта

### Локальная разработка

1. Клонирование репозитория:

```bash
git clone https://github.com/caVenikk/ITMO_glossary_service.git
cd ITMO_glossary_service
```

2. Создание виртуального окружения:

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установка зависимостей:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Для разработки
```

4. Настройка pre-commit:

```bash
pre-commit install
```

5. Применение миграций:

```bash
alembic upgrade head
```

6. Запуск сервера:

```bash
cd src
python run.py
```

### Запуск через Docker

```bash
docker-compose up --build
```

API будет доступен по адресу `http://localhost:8000/api`

## Инструменты разработки

### Качество кода

- **Ruff**: Проверка и форматирование

  ```bash
  ruff check src
  ruff format src
  ```

- **mypy**: Проверка типов

  ```bash
  mypy src
  ```

- **pre-commit**: Автоматические проверки

  ```bash
  pre-commit run --all-files
  ```

### Работа с базой данных

Создание миграции:

```bash
alembic revision --autogenerate -m "описание"
```

Применение миграций:

```bash
alembic upgrade head
```

## Документация API

После запуска доступна по адресам:

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Особенности реализации

### Валидация данных

- Проверка входных данных через Pydantic
- Пользовательские валидаторы для бизнес-логики
- Обработка ошибок с корректными HTTP-статусами

### База данных

- Асинхронный SQLAlchemy
- Паттерн Repository для доступа к данным
- Автоматические миграции через Alembic
- Загрузка начальных данных через фикстуры

### Docker

- Отдельные сервисы для API и миграций
- Проверки здоровья сервисов
- Монтирование томов для разработки
