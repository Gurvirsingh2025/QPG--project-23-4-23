from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name="homePage"),
    path('login/', views.login_view, name="login"),
    path('contect_us',views.contect_us, name="contect_us"),
    path('about_us',views.about_us, name="about_us"),
    path('generate_question_paper',views.generate_question_paper, name="generate_question_paper"),
    path('add_questions',views.add_questions, name="add_questions"),

]

