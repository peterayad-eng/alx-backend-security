from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("sensitive-action/", views.sensitive_action_view, name="sensitive_action"),
    path("health/", views.health_check, name="health_check"),
]

