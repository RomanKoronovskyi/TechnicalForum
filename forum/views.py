import os
import threading
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from google import genai

from forum.models import Question, Answer, Notification, Tag, Vote
from users.models import Profile

class QuestionListView(ListView):
    model = Question
    template_name = 'forum/question_list.html'
    context_object_name = 'questions'


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'forum/question_detail.html'
    context_object_name = 'question'


def ask_ai_background(question_id):
    try:
        question = Question.objects.get(id=question_id)

        ai_user, _ = User.objects.get_or_create(
            username="AI_Expert_Bot",
            defaults={"is_active": True}
        )

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error GEMINI_API_KEY not found in .env")
            return

        client = genai.Client(api_key=api_key)

        prompt = (
            f"Ти — досвідчений IT-експерт та модератор форуму. "
            f"Дай коротку, точну та виключно технічну відповідь на запитання розробника. "
            f"Якщо потрібно, додай приклад коду.\n\n"
            f"Заголовок запитання: {question.title}\n"
            f"Текст проблеми:\n{question.body}"
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        if response.text:
            Answer.objects.create(
                question=question,
                body=response.text,
                author=ai_user
            )

    except Exception as e:
        print(f"Error AI-agent: {e}")


@login_required
def create_question(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')

        question = Question.objects.create(
            title=title,
            body=body,
            author=request.user
        )

        threading.Thread(target=ask_ai_background, args=(question.id,)).start()

        return redirect('forum:question_detail', pk=question.pk)

    return render(request, 'forum/create_question.html')


@login_required
def create_answer(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=question_id)
        body = request.POST.get('body')

        Answer.objects.create(
            question=question,
            body=body,
            author=request.user
        )
    return redirect('forum:question_detail', pk=question_id)


@login_required
def vote_question(request, pk, vote_type):
    question = get_object_or_404(Question, pk=pk)
    val = 1 if vote_type == 'up' else -1

    existing_vote = Vote.objects.filter(user=request.user, question=question).first()

    if not existing_vote:
        Vote.objects.create(user=request.user, question=question, value=val)
        question.votes += val
        question.save()

        author_profile, _ = Profile.objects.get_or_create(user=question.author)
        author_profile.reputation += (val * 10)
        author_profile.save()

        if question.author != request.user:
            Notification.objects.create(
                user=question.author,
                text=f"Ваше запитання '{question.title}' отримало новий голос!"
            )

    return redirect('forum:question_detail', pk=question.pk)


@login_required
def accept_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)

    if answer.question.author == request.user:
        answer.question.answers.update(is_accepted=False)

        answer.is_accepted = True
        answer.save()

        author_profile, _ = Profile.objects.get_or_create(user=answer.author)
        author_profile.reputation += 15
        author_profile.save()

        Notification.objects.create(
            user=answer.author,
            answer=answer
        )

    return redirect('forum:question_detail', pk=answer.question.pk)


@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    notifications.update(is_read=True)
    return render(request, 'forum/notifications.html', {'notifications': notifications})


@login_required
def users_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Доступ заборонено. Ця панель доступна лише для суперкористувачів.")

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'forum/users_list.html', {'users_list': users})


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Доступ заборонено.")

    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, id=user_id)
        user_to_delete.delete()
    return redirect('forum:users_list')


@login_required
def delete_question(request, question_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Доступ заборонено. Ви не маєте прав для видалення контенту.")

    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        question.delete()

    return redirect('forum:question_list')