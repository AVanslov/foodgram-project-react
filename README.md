![example event parameter](https://github.com/avanslov/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

## Описание
**Сервис Foodgram - это готовый сервис для создания рецептов и выгрузки списка покупок на основе собранной пользователем корзины с рецептами.**

### Справка

Справка по API сервиса Foodgram доступна [здесь](https://foodgramius.ddns.net/api/docs/redoc.html)

В данном проекте моей главной задачей было написать API бекенда сервиса для осуществления взаимодействия с фронтендом на React.
Бекенд был мною разработан на Django REST Framework.
Тистирование API в ходе разработки я проводил в Postman.
Также в проекте я настраивал CI/CD - составлял Dockerfile, конфигурацию файлов Nginx локального и на сервере с Ubuntu (поскольку на сервере развернуто несколько проектов в контейнерах), также настраивал автоматический деплой на сервер с помощью GitHub workflows.

## Стек технологий проекта
![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/-Django-black?style=for-the-badge&logo=Django)
![DRF](https://img.shields.io/badge/-Django_REST_Framework-black?style=for-the-badge&logo=DRF)
![PostgresQL](https://img.shields.io/badge/-PostgresQL-black?style=for-the-badge&logo=PostgresQL)
![SQLite](https://img.shields.io/badge/-SQLite-black?style=for-the-badge&logo=SQLite)
![Docker](https://img.shields.io/badge/-Docker-black?style=for-the-badge&logo=Docker)
![Nginx](https://img.shields.io/badge/-Nginx-black?style=for-the-badge&logo=Nginx)
![Linux](https://img.shields.io/badge/-Linux-black?style=for-the-badge&logo=Linux)
![Postman](https://img.shields.io/badge/-Postman-black?style=for-the-badge&logo=postman)


## Установка

***Клонировать репозиторий и перейти в него в командной строке:***

```
git clone git@github.com:your_username_in_github/foodgram_project_react.git
cd foodgram_project_react/backend/foodgram_project
```

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
sudo docker compose -f exec backend python manage.py loaddata data/ingredients.json
sudo docker compose -f exec backend python manage.py loaddata data/tags.json
```

Теперь проект достпен по адресам:
[127.0.0.1](http://127.0.0.1/)
[localhost](http://localhost//)

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
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata data/ingredients.json
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata data/tags.json
```
**Развернутный проект доступен по сдресу [foodgramius.ddns.net](https://foodgramius.ddns.net/recipes)**

***Автор***
Бучельников Александр
[E-mail](mailto:a.buchelnikov99@gmail.com)
