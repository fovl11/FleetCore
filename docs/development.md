# Локальная разработка

Требования: Docker Engine с плагином Compose. Для разработки без контейнеров нужны Python 3.12 или новее и Node.js 22 или новее.

## Compose

Скопируйте `.env.example` в `.env`, затем выполните `docker compose up --build`. Compose открывает web-приложение на порту 5173, API — на порту 8000, PostgreSQL — на порту 5432. База данных использует именованный том, поэтому её данные сохраняются после перезапуска контейнеров.

## Backend без Compose

В каталоге `backend/` установите зависимости из `requirements.txt`, затем запустите `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

## Frontend без Compose

В каталоге `frontend/` выполните `npm install` и `npm run dev -- --host 0.0.0.0`. Укажите для `VITE_API_BASE_URL` адрес API (по умолчанию `http://localhost:8000`).
