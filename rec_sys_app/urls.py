from django.urls import path, re_path, include
from rec_sys_app import views

app_name = "rec_sys_app"

urlpatterns = [
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
]
