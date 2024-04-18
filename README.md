![example event parameter](https://github.com/avanslov/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)
# praktikum_new_diplom

## Описание
**Сервис Foodgram - это готовый сервис для создания рецептов и выгрузки списка покупок на основе собранной пользователем корзины с рецептами.**

### Справка

Справка по API сервиса Foodgram доступна по адресу 
https://foodgramius.ddns.net/api/docs/redoc.html

## Установка

***Клонировать репозиторий и перейти в него в командной строке:***

git clone git@github.com:your_username_in_github/foodgram_project_react.git
cd foodgram_project_react/backend/foodgram_project
Cоздать и активировать виртуальное окружение:
```

Для Windows:
python -m venv env
source venv/Script/activate

Для Linux/MacOS:
python3 -m venv env
source venv/bin/activate
```
***Установить зависимости из файла requirements.txt:***

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

***Как заполнить .env:***

POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

## Развертывание проекта

***Как зупустить проект локально***
```
cd infra/
```

Создайте или скопируйте в директорию infra/ файл .env, конфигурация которого описана выше.

Выполните сборку проекта:

```
sudo docker compose up
```

Перейдите в директорию, где лежит файл docker-compose.yml, и выполните миграции:

```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```
Соберите статику:
```
sudo docker compose -f exec backend python manage.py collectstatic
sudo docker compose -f exec backend cp -r /app/static/. /code/static/
```
Загрузите тестовые данные:

```
sudo docker compose -f exec backend python manage.py loaddata ingredients.json
sudo docker compose -f exec backend python manage.py loaddata tags.json
```

Теперь проект достпен по адресам:
http://127.0.0.1/
http://localhost/

***Как зупустить проект на вашем сервере***

На вашем сервере создайте папку проекта.
Скопируйте в нее с локального компьютера файл infra/nginx.conf .env и docker-compose.production.yml

Выполните последовательно команды ниже, чтобы создать миграции, собрать статику, переместить ее в ожидаемую директорию и наполнить БД подготовленными данными.
```
docker compose -f docker-compose.production.yml up
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /code/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata ingredients.json
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata tags.json
```

***Автор***
Бучельников Александр
e-mail: a.buchelnikov99@gmail.com


