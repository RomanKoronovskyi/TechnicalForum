from django.shortcuts import render, redirect
from django.contrib.auth import login
from users.forms import DeveloperRegistrationForm

def register(request):
    if request.method == 'POST':
        form = DeveloperRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('forum:question_list')
    else:
        form = DeveloperRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
