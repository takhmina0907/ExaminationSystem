import json

from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView as BaseLoginView, LogoutView as BaseLogoutView)
from django.contrib.auth import login
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from things.admin_forms.forms import (
    UserCreateForm, UserAuthForm, TestCreateForm,
)
from things.models import TestInfo, Question, Option


class RegistrationView(CreateView):
    form_class = UserCreateForm
    template_name = 'admin/registration.html'

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return super(RegistrationView, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('admin-tests', kwargs={'id': self.request.user.id})


class LoginView(BaseLoginView):
    form_class = UserAuthForm
    template_name = 'admin/login.html'

    def get_success_url(self):
        return reverse_lazy('admin-tests', kwargs={'id': self.request.user.id})


# TODO test logout
class LogoutView(BaseLogoutView):
    def get_next_page(self):
        return reverse_lazy('home')


class BaseAdminView(LoginRequiredMixin):
    pass


class AdminTestCreateView(BaseAdminView, CreateView):
    model = TestInfo
    form_class = TestCreateForm
    template_name = 'admin/test_create.html'

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admin-tests', kwargs={'id': self.request.user.id})


class AdminTestListView(BaseAdminView, ListView):
    model = TestInfo
    context_object_name = 'tests'
    template_name = 'admin/tests.html'

    def get_queryset(self):
        return self.request.user.tests.all()


class AdminTestDetailView(BaseAdminView, DetailView):
    model = TestInfo
    context_object_name = 'test'
    pk_url_kwarg = 'tid'
    template_name = 'admin/test.html'

    def get_queryset(self):
        return self.request.user.tests.all()


@login_required
def admin_questions_create(request, user_id, test_id):
    test = get_object_or_404(TestInfo, id=test_id, author=request.user)
    if request.is_ajax() and request.method == 'POST':
        questions = json.loads(request.body.decode('utf-8'))
        errors = []
        single_choice_options_min = 2
        single_choice_options_max = 6
        single_choice_options_correct_max = 1
        multiple_choice_options_min = 3
        multiple_choice_options_max = 8
        multiple_choice_options_correct_min = 2

        if not len(questions) > 0:
            errors.append(
                {
                    'error': 'Test does not have any questions'
                }
            )

        for index in range(0, len(questions)):
            question = questions[index]
            options_len = len(question['options'])

            if not options_len > 0:
                errors.append(
                    {
                        'error': 'Question does not have any options',
                        'question': index,
                    }
                )
                continue

            if question['is_multiple_choice']:
                if options_len < multiple_choice_options_min:
                    errors.append({
                        'error': 'Multiple choice question should have at least {} options'.
                            format(multiple_choice_options_min),
                        'question': index,
                    })
                    continue
                elif options_len > multiple_choice_options_max:
                    errors.append({
                        'error': 'Multiple choice question can\'t have more than {} options'.
                            format(multiple_choice_options_max),
                        'question': index,
                    })
                    continue
            else:
                if options_len < single_choice_options_min:
                    errors.append({
                        'error': 'Single choice question should have at least {} options'.
                            format(single_choice_options_min),
                        'question': index,
                    })
                    continue
                elif options_len > single_choice_options_max:
                    errors.append({
                        'error': 'Single choice question can\'t have more than {} options'.
                            format(single_choice_options_max),
                        'question': index,
                    })
                    continue

            correct_options = 0
            for option in question['options']:
                if option['is_correct']:
                    correct_options += 1

            if question['is_multiple_choice']:
                if correct_options < multiple_choice_options_correct_min:
                    errors.append({
                        'error': 'Multiple choice question should have at least {} correct options'.
                            format(multiple_choice_options_correct_min),
                        'question': index,
                    })
                    continue
            else:
                if correct_options == 0:
                    errors.append({
                        'error': 'Single choice question should have {} correct option'.
                            format(single_choice_options_correct_max),
                        'question': index,
                    })
                    continue
                if correct_options > single_choice_options_correct_max:
                    errors.append({
                        'error': 'Single choice question can\'t have more than {} correct option'.
                            format(single_choice_options_correct_max),
                        'question': index,
                    })
                    continue

        if len(errors) > 0:
            return JsonResponse({'response': json.dumps(errors)}, status=400)
        else:
            for obj in questions:
                question = Question.objects.create(test=test,
                                                   question=obj['question'],
                                                   is_multiple_choice=obj['is_multiple_choice'])
                question.save()
                for opt in obj['options']:
                    option = Option.objects.create(question=question,
                                                   option=opt['option'],
                                                   is_correct=opt['is_correct'])
                    option.save()
        return JsonResponse({'response': "Questions were successfully created"}, status=200)

    return render(request, 'admin/question_populate.html', {'test': test})


@login_required
def admin_test(request, user_id, test_id):
    test = get_object_or_404(TestInfo, id=test_id, author=request.user)

    if test.questions.count() == 0:
        question = Question.objects.create(test=test, question='Enter the question', is_multiple_choice=False)
        Option.objects.create(question=question, option='Option 1', is_correct=False)
        Option.objects.create(question=question, option='Option 2', is_correct=False)

    return render(request, 'admin/question_create.html', {'test': test, 'questions': test.questions.all()})


@login_required
def admin_question_add(request, user_id, test_id):
    test = get_object_or_404(TestInfo, id=test_id, author=request.user)

    if request.is_ajax() and request.method == 'POST':
        question = Question.objects.create(test=test, question='Enter the question', is_multiple_choice=False)
        option_1 = Option.objects.create(question=question, option='Option 1', is_correct=False)
        option_2 = Option.objects.create(question=question, option='Option 2', is_correct=False)
        return JsonResponse(json.dumps({
                                'id': question.id,
                                'question': question.question,
                                'options': [
                                    {
                                        'id': option_1.id,
                                        'option': option_1.option,
                                        'is_correct': option_1.is_correct,
                                    },
                                    {
                                        'id': option_2.id,
                                        'option': option_2.option,
                                        'is_correct': option_2.is_correct,
                                    }
                                ]
                            }),
                            safe=False,
                            status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)


@login_required
def admin_question_update(request, user_id, test_id, question_id):
    if request.is_ajax() and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question = Question.objects.get(id=data['id'])
        question_changed = False
        if question.question != data['question']:
            question.question = data['question']
            question_changed = True

        correct_count = 0
        for opt in data['options']:
            option = Option.objects.get(id=opt['id'])
            changed = False
            if option.option != opt['option']:
                option.option = opt['option']
                changed = True

            if option.is_correct != opt['is_correct']:
                option.is_correct = opt['is_correct']
                changed = True

            if opt['is_correct']:
                correct_count += 1

            if changed:
                option.save()
        print(correct_count)
        if not question.is_multiple_choice and correct_count > 1:
            question.is_multiple_choice = True
            question_changed = True

        if question.is_multiple_choice and correct_count < 2:
            question.is_multiple_choice = False
            question_changed = True

        if question_changed:
            question.save()

        question.save()

        return JsonResponse({'response': 'Question was successfully saved'}, status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)


@login_required
def admin_option_add(request, user_id, test_id, question_id):
    if request.is_ajax() and request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        option = Option.objects.create(
            question=question,
            option='Option {}'.format(question.options.count()+1),
            is_correct=False
        )
        return JsonResponse(json.dumps({'id': option.id,
                                        'question_id': question.id,
                                        'option': option.option,
                                        'is_correct': option.is_correct,
                                        }),
                            safe=False,
                            status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)
