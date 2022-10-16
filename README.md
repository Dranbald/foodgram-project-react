![yamdb_workflow](https://github.com/Dranbald/foodgram-project-react/actions/workflows/workflow_for_foodgram.yml/badge.svg)

# Проект Foodgram

#### Проект доступен по адресу - http://51.250.25.115/

## О проекте

Проект Foodgram собирает кулинарные рецепты разных пользователей, что позволяет им делиться своими уникальными или фирменными рецептами друг с другом.

Возможности проекта Foodgram позволяют пользователю:

- Создавать и редактировать свои рецепты

- Добавлять рецепты в избранное

- Подписываться на определенных авторов

- Добавлять рецепты в список покупок

- Загружать список покупок к себе на устройство в виде текстового файла, где будут указаны необходимые ингредиенты для всех добавленных, в список покупок, рецептов


## Список библиотек

Python, Django, Git, PostgreSQL, Docker


## Шаблон наполнения env-файла

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```


## Запуск приложения в контейнерах
#### 1. Клонировать репозиторий:

> <sub> https://github.com/Dranbald/foodgram-project-react </sub>  

> <sub> cd foodgram-project-react/infra </sub>

#### 2. Запуск docker-compose:

> <sub> docker-compose up -d </sub> 

#### 3. Выполнить миграции:

> <sub> docker-compose exec web python manage.py migrate </sub> 

#### 4. Создать суперпользователя:

> <sub> docker-compose exec web python manage.py createsuperuser </sub> 

#### 5. Подключить статику:

> <sub> docker-compose exec web python manage.py collectstatic --no-input </sub> 

## Заполнение базы данными:

> <sub> docker-compose exec web python manage.py loaddata dump.json </sub> 


---
## Автор

[Захаров Данил](https://github.com/Dranbald) - backend, студент Яндекс Практикум.

[Яндекс.Практикум](https://github.com/yandex-praktikum) - frontend.
