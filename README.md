# Тестовое задание: Backend на FastAPI

Асинхронный REST API для пользователей, администраторов, счетов и платежей.

**Стек:**

- Python 3.12+, FastAPI, SQLAlchemy (async), PostgreSQL
- Docker Compose
- Poetry

**Функционал:**

- Пользователь: регистрация, авторизация, просмотр счетов и платежей
- Администратор: CRUD пользователей, просмотр счетов
- Платежи: пополнение счета, обработка вебхука, проверка подписи

**Swagger-документация:**

- Swagger UI доступен по адресу [`/api/docs`](http://localhost:8000/api/docs) после запуска приложения.

**Запуск:**

- Через Docker Compose:
    ```
    docker-compose up --build
    ```
- Локально:
    - Через Makefile:
        ```
        make install
        make run
        ```
    - Без Makefile:
        ```
        poetry install
        poetry run python -m app
        ```

**Тестовые данные для входа:**

- **Клиент**
    - Логин: `client1@example.com`
    - Пароль: `clientpass`

- **Админ**
    - Логин: `admin1@example.com`
    - Пароль: `adminpass`
