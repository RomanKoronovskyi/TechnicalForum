from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class DeveloperRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Логін",
        help_text="Обов'язково. Максимум 150 символів. Дозволено літери, цифри та знаки @/./+/-/_."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].label = "Пароль"
        if 'password2' in self.fields:
            self.fields['password2'].label = "Підтвердження пароля"
        if 'password2' in self.fields:
            self.fields['password2'].help_text = "Введіть такий самий пароль, як і вище"
        if 'password1' in self.fields:
            self.fields['password1'].help_text = (
                "<ul>"
                "<li>Пароль не може бути занадто схожим на вашу особисту інформацію.</li>"
                "<li>Пароль має містити щонайменше 8 символів.</li>"
                "<li>Пароль не може бути поширеним (шаблонним).</li>"
                "<li>Пароль не може складатися виключно з цифр.</li>"
                "</ul>"
            )
