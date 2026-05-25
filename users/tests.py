from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile
from users.forms import DeveloperRegistrationForm


class UsersModuleTestCase(TestCase):
    def setUp(self):
        self.username = "test_developer"
        self.password = "SecurePass12345"

    def test_user_registration_and_profile_signal(self):
        user = User.objects.create_user(username=self.username, password=self.password)

        self.assertEqual(User.objects.count(), 1)

        profile_exists = Profile.objects.filter(user=user).exists()
        self.assertTrue(profile_exists, "Профіль не був створений автоматично через сигнал post_save!")

        if profile_exists:
            profile = Profile.objects.get(user=user)
            self.assertEqual(profile.reputation, 0, "Початкова репутація розробника має дорівнювати 0.")

    def test_profile_cascade_deletion(self):
        user = User.objects.create_user(username=self.username, password=self.password)
        self.assertEqual(Profile.objects.count(), 1)

        user.delete()
        self.assertEqual(Profile.objects.count(), 0,
                         "Таблиця users_profile містить застарілі дані після видалення користувача!")

    def test_developer_registration_form_labels(self):
        form = DeveloperRegistrationForm()

        self.assertEqual(form.fields['password1'].label, "Пароль")
        self.assertEqual(form.fields['password2'].label, "Підтвердження пароля")

    def test_developer_registration_form_invalid_data(self):
        form_data = {
            'username': 'valid_dev',
            'password1': 'Password123',
            'password2': 'DifferentPassword123'
        }
        form = DeveloperRegistrationForm(data=form_data)

        self.assertFalse(form.is_valid(), "Форма пропустила реєстрацію, хоча паролі не збігаються!")

        self.assertIn('password2', form.errors)