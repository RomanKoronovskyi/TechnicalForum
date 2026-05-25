from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question


class TechnicalForumTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='dev_user', password='password123')

        self.admin_user = User.objects.create_superuser(username='admin_user', password='adminpassword123')

        self.question = Question.objects.create(
            title="How to configure volumes in Docker Compose?",
            body="Error accessing the postgres_data dir",
            author=self.user
        )


    def test_question_list_view_accessible(self):
        response = self.client.get(reverse('forum:question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/question_list.html')

    def test_question_detail_view_accessible(self):
        response = self.client.get(reverse('forum:question_detail', args=[self.question.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/question_detail.html')


    def test_create_question_requires_login(self):
        response = self.client.get(reverse('forum:create_question'))
        self.assertEqual(response.status_code, 302)

    def test_create_question_authenticated(self):
        self.client.login(username='dev_user', password='password123')

        response = self.client.post(reverse('forum:create_question'), {
            'title': 'Question about Nginx',
            'body': 'Tell me about Nginx',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 2)


    def test_users_list_forbidden_for_regular_user(self):
        self.client.login(username='dev_user', password='password123')
        response = self.client.get(reverse('forum:users_list'))
        self.assertEqual(response.status_code, 403)

    def test_users_list_allowed_for_superuser(self):
        self.client.login(username='admin_user', password='adminpassword123')
        response = self.client.get(reverse('forum:users_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/users_list.html')


    def test_vote_question_up(self):
        self.client.login(username='dev_user', password='password123')
        response = self.client.post(reverse('forum:vote_question', args=[self.question.pk, 'up']))
        self.assertEqual(response.status_code, 302)

        self.question.refresh_from_db()
        self.assertEqual(self.question.votes, 1)
