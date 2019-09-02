from django.urls import path, re_path, include
from rec_sys_app import views

app_name = "rec_sys_app"

urlpatterns = [
    path("login", views.user_login, name="user_login"),
    path("logout", views.user_logout, name="user_logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("index", views.index, name="index"),
]
