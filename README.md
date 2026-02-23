# Справочная система поддержки малого бизнеса

Production-ready система на Python 3.12+ с SQLAlchemy ORM:
- CLI интерфейс
- Web GUI (Flask + Bootstrap 5)
- REST API (Flask + JWT)

## Возможности

- Регистрация и вход пользователей
- Роли: предприниматель, консультант, администратор
- База знаний: просмотр, поиск, фильтрация, CRUD статей
- Q&A: вопросы и ответы
- Админ-панель: управление пользователями
- Безопасность: bcrypt-хеширование паролей, валидация, разграничение прав

## Быстрый запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Запуск после скачивания с GitHub

1. Клонировать проект и перейти в папку:
```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd PZIIS-lab1
```

2. Создать виртуальное окружение и установить зависимости:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Проверить `.env` (при необходимости изменить ключи):
```bash
cat .env
```

4. Запустить Web GUI (Flask):
```bash
export FLASK_APP=web.app:create_app
flask run
```

5. Открыть в браузере:
- Web: `http://127.0.0.1:5000`

## Запуск REST API

```bash
source .venv/bin/activate
export FLASK_APP=api.app:create_app
flask run --port 5001
```

- API base URL: `http://127.0.0.1:5001/api`

## Запуск через Docker

```bash
docker-compose up --build
```

- Web (Gunicorn): `http://127.0.0.1:8000`
- PostgreSQL: `localhost:5432`

## Переменные окружения

- `DATABASE_URL` (по умолчанию `sqlite:///business_help.db`)
- `LOG_LEVEL` (по умолчанию `INFO`)
- `SECRET_KEY` (секрет Flask-сессий)
- `JWT_SECRET_KEY` (секрет JWT токенов API)

## Дефолтный администратор

- Логин: `admin`
- Пароль: `Admin123!`
