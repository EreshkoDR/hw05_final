# Проект социальной сети "YaTube"

## Описание:
Проект представляет из себя социальную сеть. Имеются следующие возможности:

- Регистрация и создание профиля пользователя с личным кабинетом.
- ~~Создание, чтение, редактирование и удаление~~ CRUD для постов и комментариев к ним.
- Подписка на авторов
- Возможность загружать изображения

## Технологии:
- Python 3.9
- Django 2.2.16
- SQLite

## Развертка проекта
После клонирования репозитория вам потребуется создать виртуальное окружение, установить зависимости, выполнить миграции и создать суперпользователя.

### Виртуальное окружение и зависимости
- Для создания виртуального окружения выполните команду `python3 -m venv venv`
- Установка зависимостей `pip3 -r requirements.txt`

### Миграции и суперпользователь
- Перейдите в каталог yatube `cd yatube`
- Выполните миграции `python3 manage.py migrate`
- Создайте суперпользователя `python3 manage.py createsuperuser` 
> При создании суперпользователя опционально можно указать email

### Запуск django
- Для локального запуска выполните команду `python3 manage.py runserver`
- Проект запустится по адресу `127.0.0.1:8000`
> Опционально порт можно изменить присвоив аргумент к runserver `python3 manage.py runserver xx.xx.xx.xx:you_port`, где "x" ваш ip4 адрес
>> Либо, можно указать локальный адрес: `python3 manage.py runserver 0:you_port`
