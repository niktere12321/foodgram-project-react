# Проект Foodgram
[![food workflow](https://github.com/niktere12321/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/niktere12321/foodgram-project-react/actions/workflows/main.yml)

## Описание проекта

Foodgram это ресурс для публикации рецептов.  
Пользователи могут создавать свои рецепты, читать рецепты других пользователей, подписываться на интересных авторов, добавлять лучшие рецепты в избранное, а также создавать список покупок и загружать его в pdf формате

## Установка проекта локально

* Склонировать репозиторий на локальную машину:
```bash
git clone https://github.com/niktere12321/foodgram-project-react.git
```
```bash
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```bash
python -m venv env
```

```bash
source venv/Scripts/activate
```

* Cоздайте файл `.env` в директории `/infra/` с содержанием:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Перейти в директирию и установить зависимости из файла requirements.txt:

```bash
cd backend/
```
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

* Выполните миграции:

```bash
python manage.py migrate
```

* Запустите сервер:
```bash
python manage.py runserver
```

## Запуск проекта в Docker контейнере
* Установите Docker.

Параметры запуска описаны в файлах `docker-compose.yml` и `nginx.conf` которые находятся в директории `infra/`.  
При необходимости добавьте/измените адреса проекта в файле `nginx.conf`

* Запустите docker compose:
```bash
docker-compose up -d --build
```  
  > После сборки появляются 4 контейнера:
  > 1. контейнер базы данных **db**
  > 2. контейнер бекэнда **backend**
  > 3. контейнер web-сервера **nginx**
  > 4. контейнер фронтэнда **frontend**
* Примените миграции:
```bash
sudo docker compose exec backend python manage.py makemigrations users
sudo docker compose exec backend python manage.py migrate users
sudo docker compose exec backend python manage.py makemigrations recipe
sudo docker compose exec backend python manage.py migrate recipe
sudo docker compose exec backend python manage.py migrate
```
* Загрузите ингредиенты:
```bash
sudo docker compose exec backend python manage.py load_data ingredients.json
```
* Создайте администратора:
```bash
sudo docker compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```bash
sudo docker compose exec backend python manage.py collectstatic --noinput
```

---
## Техническая информация

Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

---
## Об авторе

Терехов Никита Алексеевич
