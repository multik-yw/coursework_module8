# Habit Tracker

## Описание

Habit Tracker — это приложение для отслеживания привычек, позволяющее пользователям создавать, управлять и отслеживать свои привычки. Приложение использует Django, PostgreSQL и Celery для управления задачами.

## Установка

### Предварительные требования

- Установленный [Docker](https://docs.docker.com/get-docker/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

### Настройка локальной среды

1. **Клонируйте репозиторий**:
- git clone https://github.com/multik-yw/coursework_module8.git

2. **Создайте файл .env в корне проекта и добавьте необходимые переменные окружения**:
  SECRET_KEY=<ваш-secret-key>;
  POSTGRES_DB=<имя-бд>;
  POSTGRES_USER=<пользователь-бд>;
  POSTGRES_PASSWORD=<пароль-бд>;

4. **Запустите проект:**
docker-compose up --build

5. **Примените миграции:**
docker-compose exec web python manage.py migrate

6. **После успешного запуска приложения, оно будет доступно по адресу** http://localhost:8000.

**Для запуска тестов используйте следующую команду:**
docker-compose run web python manage.py test

### Деплой на сервер
1. Убедитесь, что сервер готов к работе с Docker и Docker Compose.
2. Настройте SSH-доступ к серверу.
3. При каждом пуше в ветку main проект автоматически разворачивается на сервере.

