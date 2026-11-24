# FleetCore

FleetCore — стартовая система управления автопарком с React-клиентом, API на FastAPI и PostgreSQL, запускаемая через Docker Compose.

## Быстрый запуск с Docker Compose

1. Скопируйте `.env.example` в `.env`.
2. Сгенерируйте закрытый ключ подписи JWT и укажите полученное значение в `JWT_SECRET_KEY` файла `.env`. PowerShell: `$bytes = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString("x2") })`. В рабочей среде включите `AUTH_COOKIE_SECURE=true` при использовании HTTPS.
3. Запустите `docker compose up --build -d`.
4. Примените миграции схемы: `docker compose exec backend alembic upgrade head`.
5. Откройте frontend по адресу <http://localhost:5173>, документацию API — по адресу <http://localhost:8000/docs>, а проверку готовности — по адресу <http://localhost:8000/api/v1/health>.
6. Запустите тесты backend командой `docker compose exec backend python -m pytest -v`.

Миграции запускаются явно и не выполняются при старте приложения. Храните `.env` в безопасности и не добавляйте реальные учётные данные или ключи JWT в систему контроля версий.

## API аутентификации

- `POST /api/v1/auth/register` принимает email, password, organization_name и необязательный display_name; создаёт членство пользователя с ролью владельца.
- `POST /api/v1/auth/login` принимает email и password.
- Вход и регистрация возвращают краткосрочный access token. Ротируемый refresh JWT хранится в cookie с атрибутами HttpOnly и SameSite=Strict.
- `POST /api/v1/auth/refresh` ротирует refresh cookie и возвращает новый access token.
- `POST /api/v1/auth/logout` отзывает текущую refresh-сессию и удаляет cookie.
- `GET /api/v1/auth/me` требует заголовок `Authorization: Bearer <access_token>` и возвращает текущую организацию и роль пользователя.

Срок действия access token — 15 минут, refresh-сессии — 7 дней. Refresh JWT подписываются, а их идентификаторы сессий хранятся в PostgreSQL, что позволяет ротировать и отзывать их. Для защищённых запросов членство пользователя в организации проверяется повторно.

## Разработка backend без Compose

Требуется Python 3.12 или новее. В каталоге `backend/` создайте и активируйте виртуальное окружение, затем выполните `python -m pip install -r requirements.txt`. Укажите для `DATABASE_URL` URL PostgreSQL в формате SQLAlchemy, а для `JWT_SECRET_KEY` — случайно сгенерированный ключ длиной не менее 32 байт. Выполните `alembic upgrade head`, затем `uvicorn app.main:app --reload`. Запустите тесты командой `python -m pytest -v`.

## Репозиторий

См. [AGENTS.md](AGENTS.md) и [docs/architecture.md](docs/architecture.md).
