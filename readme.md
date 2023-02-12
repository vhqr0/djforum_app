# DJForum

A lightweight forum based on Django.

## Installation

### Install dependences

```bash
# Pillow, Django, django-registation-redux
pip install -r requirements.txt
```

### Create project

```bash
django-admin startproject xxx\_proj
```

Move this repo to the root of the project, like this: xxx\_proj/djforum_app.

### Install apps

Add apps to `INSTALLED_APPS` in xxx\_proj/xxx\_proj/settings.py, like this:

```python
INSTALLED_APPS = [
    "djforum_app",
    "registration",
    # other apps...
]
```

Notice: add to the beginning ot the list to override builtin templates.

### Add settings

Add settings in the end of settings.py:

```python
# email backend, for test
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# login related url
LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'

# registration settings
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
```

You may also want to add or change other settings, see Django documentation.

### Add routes

Add route to `urlpatterns` in xxx\_proj/urls.py:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('registration.backends.default.urls')),
    path('djforum/', include('djforum_app.urls')),
]
```

You may also want to redirect root to the djforum index page, like this:

```python
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('djforum:index')),
    # other routes...
]
```

### Start project

```bash
./manage.py runserver
```

You may also want to add a super user before start:

```bash
./manage.py createsuperuser
```
