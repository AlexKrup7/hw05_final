# hw05_final
### Учебный проект hw05_final
***
### Возможности:
#### Стандартные:
* создание постов с картинками
* комментирование постов
* подписка на автора поста
***
### Как запустить проект:
```
https://github.com/AlexKrup7/hw05_final.git
```
Создать и активировать виртуальное окружение:
```
python -m venv env

source venv/bin/activate
```
Обновить pip
```
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить сервер:
```
python manage.py runserver
```
Ссылка на локальный сервер:
http://127.0.0.1:8000/

Документация доступна по адресу:
http://127.0.0.1:8000/redoc/
