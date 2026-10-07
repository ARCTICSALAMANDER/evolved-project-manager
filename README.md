# Менеджер проектов 
Менеджер проектов, призванный упростить разбиение идеи на мелкие задачи и отслеживать свои идеи через карту мыслей.

## Функционал
Этот менеджер проектов позволяет адаптировать рабочее пространство под конкретные задачи. Вы можете сами выбрать нужные функции и добавить их на панель инструментов. Например, сервис позволяет использовать нейросеть, чтобы разделить общую идею на мелкие таски. В системе удобно вести списки дел, создавать карты мыслей и настраивать доступ к проектам для других пользователей.

### Что реализовано сейчас:
1. Разбиение большой задачи на более мелкие таски с помощью ИИ (через ollama)
2. REST API сервиса с CRUD функционалом
3. Создание JWT токенов для аутентификации
4. Хэширование паролей пользователей с bcrypt
5. Refresh-токены
6. Асинхронная база данных с поддержкой миграций
7. Профиль с email и технологическим стеком, ссылка на репозиторий проекта и полный набор полей задачи со статусами, исполнителем и ссылкой на commit/PR

### Что будет реализовано:
1. Фронтенд сервиса на TypeScript + React
2. Карта мыслей (mind map) для визуализации проектов

## Стек технологий
Бэкенд: FastAPI, Uvicorn, httpx (запросы к Ollama)  
Аутентификация: jose (jwt), bcrypt 
БД: sqlalchemy (core), postgresql, asyncpg, Alembic
ИИ: qwen3:4b через ollama

Фронтенд: TypeScript + React + Vite, Tailwind CSS (планируемый стек)

## Предварительные требования
1. Python 3.10+
2. PostgreSQL 12+
3. Ollama (для функций ИИ)
4. pip (менеджер пакетов Python)

## Установка и запуск

### 1. Установка зависимостей Python
```bash
pip install -r requirements.txt
```

### 2. Подготовка переменных окружения
Отредактируйте файл `.env` в корне проекта с учетом вашей конфигурации:
```env
DB_PASSWORD=your_db_password
DB_USER=postgres
HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/project_manager
JWT_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
AI_URL=http://localhost:11434
```

### 3. Подготовка базы данных
Убедитесь, что PostgreSQL запущен, создайте базу данных:
```bash
createdb project_manager
```

Примените миграции:
```bash
cd backend
alembic upgrade head
cd ..
```

### 4. Запуск Ollama, в отдельном терминале
```bash
ollama serve
```

### 5. Запуск сервера
```bash
python run.py
```

Сервер запустится на `http://localhost:8000`

Документация API:
Swagger UI: http://localhost:8000/docs

## Структура проекта
```
evolved project manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API маршруты
│   │   ├── core/         # Конфигурация и безопасность
│   │   ├── db/           # БД слой
│   │   ├── schemas/      # Pydantic модели
│   │   ├── services/     # AI сервис
│   │   └── main.py       # FastAPI приложение
│   ├── migrations/       # Alembic миграции
│   └── alembic.ini       # Конфиг Alembic
├── frontend/             # в разработке
├── requirements.txt      # Python зависимости
├── run.py               # Точка входа для запуска сервера
└── .env                 # Переменные окружения
```

## Структура API
1. Проекты: /api/projects - crud проектов
2. Задачи: /api/tasks - crud задач в проектах
3. Пользователи: /api/users - crud профилй пользователей
4. Аутентификация: /api/auth - регистрация, вход, refresh токены
5. ИИ: /api/ai - разбиение задач на таски с помощью ИИ

Профиль текущего пользователя доступен через `GET /api/users/profile` и обновляется через `PATCH /api/users/update` (поля `new_username`, `email`, `tech_stack`). Стек передается списком строк. Ссылка на репозиторий задается полем `repository_url`; API возвращает ее только владельцу проекта и его участникам. Статусы задач: `not_started`, `in_progress`, `review`, `completed`; ссылка на commit или pull request хранится в `commit_url`.