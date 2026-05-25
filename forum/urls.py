from django.urls import path
from .views import (
    QuestionListView, QuestionDetailView, create_question,
    create_answer, vote_question, accept_answer, notifications_list,
    users_list, delete_user,
    register
)

app_name = 'forum'

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),
    path('question/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    path('question/new/', create_question, name='create_question'),
    path('question/<int:question_id>/answer/', create_answer, name='create_answer'),
    path('question/<int:pk>/vote/<str:vote_type>/', vote_question, name='vote_question'),
    path('answer/<int:pk>/accept/', accept_answer, name='accept_answer'),
    path('notifications/', notifications_list, name='notifications_list'),
    path('users/', users_list, name='users_list'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('register/', register, name='register'),
]