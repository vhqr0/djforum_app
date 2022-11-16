* DJForum

A lightweight forum based on Django.

** Installation

1. You should install `Django` and `Pillow` from `pip` at first.
2. Then, create a django project, such as `django-admin startproject xxx_proj`.
3. Clone this repo to the project, the root such as `xxx_proj/djforum_app/`.
4. Edit `xxx_proj/xxx_proj/settings.py`, add `"djforum_app"` to `INSTALLED_APPS`.
5. Config email backend for the project. For test purpose such as `EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'`.
6. Put the route of djforum to global route `xxx_proj/xxx_proj/urls.py` `urlpatterns`, such as `path('djforum/', include('djforum_app.urls'))`.

ps.1. Any question, see Djnago's Document.
ps.2. You may want to redirect the root route to the djforum index page, such as `path('', lambda request: redirect('djforum:index'))`.
