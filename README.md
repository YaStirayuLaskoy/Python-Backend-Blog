# Python Backend Blog

### Ссылка на сайт: https://webhueb.pythonanywhere.com/

## Описание

Python Backend Blog - это веб-приложение, разработанное для создания и управления личным блогом.

Приложение предоставляет удобный интерфейс пользователя, позволяющий зарегистрироваться, создавать посты, комментировать их, прикреплять изображения и подписываться на интересующих авторов.

## Основные функции
- Регистрация и аутентификация: Пользователи могут создать свои учетные записи, вводя необходимую информацию. Аутентификация осуществляется с использованием безопасных механизмов, обеспечивающих защиту данных.
- Создание и редактирование постов: Пользователи могут создавать собственные посты, добавлять заголовки, текст и прикреплять изображения. Также имеется возможность редактирования или удаления опубликованных постов.
- Комментирование постов: Зарегистрированные пользователи могут оставлять комментарии к постам других авторов, что позволяет взаимодействовать и обсуждать интересные темы.
- Подписка на авторов: Пользователи могут подписываться на понравившихся авторов блога, чтобы быть в курсе их последних постов и обновлений.
- Удобный интерфейс и навигация: Веб-приложение обладает интуитивно понятным интерфейсом, облегчающим навигацию по различным разделам блога и нахождение необходимой информации.

## Технологии и инструменты
- Python: Основной язык программирования, используемый для разработки бэкенда.
- Фреймворк Django: Облегчает создание веб-приложений и API с использованием Python.
- База данных: Хранение данных о пользователях, постах, комментариях и подписках осуществляется с использованием MySQL.
- HTML и CSS: Используются для создания пользовательского интерфейса и взаимодействия с веб-приложением.
- Библиотека Unittest: Для написания и выполнения модульных тестов.

## Как запустить проект

#### Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:YaStirayuLaskoy/Python-Backend-Blog.git
```
#### Перейти во внутреннюю директорию:
```
cd yatube
```
#### Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
#### Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
```
python -m pip install --upgrade pip
```
#### Провести миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```
#### Запустить проект:
```
python manage.py runserver
```
