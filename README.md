# laba_6_Oganov_A_Django_test

Django-блог со статьями о Винсенте ван Гоге, Леонардо да Винчи и
Микеланджело. Фотографии находятся в папке `photo`. Открытие страницы
статьи увеличивает счетчик просмотров.

## Запуск

Из папки `django_blog` установите Django и запустите сервер:

```powershell
cd django_blog
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000/.

## Тесты

```powershell
cd django_blog
python manage.py test blog
```
