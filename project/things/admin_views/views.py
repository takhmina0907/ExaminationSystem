import json
import io
import csv

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView as BaseLoginView, LogoutView as BaseLogoutView)
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.db.models import Avg, F, Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, RedirectView

from things.admin_forms.forms import (
    UserCreateForm, UserAuthForm, TestCreateForm, StudentCreateForm, StudentEditForm
)
from things.models import TestInfo, Question, Option, User, Student, TestResult, Speciality
from things.utils.tasks import send_mail_wrapper
from things.utils.activation_token import activation_token


class RegistrationView(CreateView):
    form_class = UserCreateForm
    template_name = 'admin/registration.html'

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.object = form.save()
        context = {
            'domain': get_current_site(self.request),
            'uidb64': urlsafe_base64_encode(force_bytes(self.object.pk)),
            'token': activation_token.make_token(self.object),
        }
        html_message = render_to_string('admin/email_activation.html', context)
        send_mail_wrapper('Welcome to Questionnaire System! Confirm your email', '',
                          self.object.email, html_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return super(RegistrationView, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('admin-pre-activation')


class PreActivationView(TemplateView):
    template_name = 'admin/pre_activation.html'


class ActivationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user_id = force_text(urlsafe_base64_decode(kwargs['uidb64']))
        return reverse_lazy('admin-tests', kwargs={'id': user_id})

    def get(self, request, *args, **kwargs):
        user = None
        try:
            user_id = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(id=user_id)
            correct = True
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            correct = False

        if correct and activation_token.check_token(user, kwargs['token']):
            user.is_email_confirmed = True
            user.save()
            login(request, user)
            return super().get(request, *args, **kwargs)
        else:
            messages.error(self.request, 'Confirmation link is invalid')
            return HttpResponseRedirect(reverse_lazy('admin-login'))


class LoginView(BaseLoginView):
    form_class = UserAuthForm
    template_name = 'admin/login.html'

    def get_success_url(self):
        return reverse_lazy('admin-tests', kwargs={'id': self.request.user.id})


class LogoutView(BaseLogoutView):
    def get_next_page(self):
        return reverse_lazy('admin-login')


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
        return reverse('admin-test', kwargs={'user_id': self.request.user.id,
                                             'test_id': self.object.id})


class TestDeleteView(BaseAdminView, DeleteView):
    model = TestInfo
    pk_url_kwarg = 'test_id'

    def get_queryset(self):
        return self.request.user.tests.all()

    def get_success_url(self):
        return reverse_lazy('admin-tests', kwargs={'id': self.kwargs['user_id']})

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        messages.success(self.request, 'You have deleted %s test successfully'
                         % test.title)
        return super(TestDeleteView, self).delete(request, *args, **kwargs)


class TestEditView(BaseAdminView, UpdateView):
    form_class = TestCreateForm
    template_name = 'admin/test_edit.html'
    context_object_name = 'test'
    pk_url_kwarg = 'test_id'

    def get_object(self, queryset=None):
        return get_object_or_404(TestInfo, author=self.request.user,
                                 id=self.kwargs['test_id'])

    def get_success_url(self):
        return reverse_lazy('admin-test-details', kwargs={'user_id': self.request.user.id,
                                                          'test_id': self.object.id})


@login_required
def copy_test(request, user_id, test_id):
    test = get_object_or_404(TestInfo, author=request.user,
                             id=test_id)
    test.id = None
    test.title = test.title + ' - Copy'
    test.save()
    return HttpResponseRedirect(reverse_lazy('admin-test-details', kwargs={'user_id': request.user.id,
                                                                           'test_id': test.id}))


class AdminTestListView(BaseAdminView, ListView):
    model = TestInfo
    context_object_name = 'tests'
    template_name = 'admin/tests.html'

    def get_queryset(self):
        return self.request.user.tests \
            .annotate(average_points=Avg('results__grade'))

    def get_context_data(self, **kwargs):
        context = super(AdminTestListView, self).get_context_data(**kwargs)
        context['test_state'] = TestInfo.TestState.__members__
        return context


class AdminTestDetailView(BaseAdminView, DetailView):
    model = TestInfo
    context_object_name = 'test'
    pk_url_kwarg = 'test_id'
    template_name = 'admin/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['average_points'] = self.get_object().results.aggregate(Avg('grade')).get('grade__avg')
        return context

    def get_queryset(self):
        return self.request.user.tests.all()


@login_required
def students_results(request, test_id, sort_by):
    if request.is_ajax() and request.method == 'POST':
        test = get_object_or_404(TestInfo, author=request.user.id,
                                 id=test_id)
        results = test.students.all().annotate(points=F('results__grade')) \
            .annotate(result_id=F('results__id'))
        if sort_by == 'student-name':
            results = results.order_by('first_name', 'last_name')
        elif sort_by == 'student-group':
            results = results.order_by('speciality')
        elif sort_by == 'student-point-ascending':
            results = results.order_by('points')
        elif sort_by == 'student-point-descending':
            results = results.order_by('-points')
        context = list()
        for result in results.values():
            context.append(result)
        return JsonResponse(json.dumps(context, cls=DjangoJSONEncoder), safe=False, status=200)
    return JsonResponse({'error': 'ajax request is required'}, status=400)


class StudentResultDetailView(BaseAdminView, DetailView):
    model = TestResult
    context_object_name = 'result'
    pk_url_kwarg = 'result_id'
    template_name = 'admin/student_result.html'

    def get_queryset(self):
        test = get_object_or_404(TestInfo, author=self.request.user,
                                 id=self.kwargs['test_id'])
        return test.results.all()


class StudentListView(BaseAdminView, ListView):
    model = Student
    context_object_name = 'students'
    template_name = 'admin/students.html'

    def get_queryset(self):
        return Student.objects.all()


class StudentDetailView(BaseAdminView, DetailView):
    model = Student
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    template_name = 'admin/student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = self.object.tests.all().annotate(point=F('results__grade')) \
            .annotate(question_rate=Count('results__answers', filter=Q(results__answers__answer__is_correct=True)))
        return context

    def get_queryset(self):
        return Student.objects.all()


class StudentCreateView(BaseAdminView, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = 'admin/student_create.html'

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.object = form.save()
        title = self.object.speciality.strip().upper()
        speciality = Speciality.objects.filter(title=title)
        if not speciality.exists():
            Speciality.objects.create(title=title)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('admin-create-student-success')


@login_required
def check_speciality(request):
    if request.is_ajax() and request.method == 'GET':
        speciality = request.GET['title'].strip().upper()
        matches = Speciality.objects.filter(
            title__startswith=speciality
        ).values('title')
        return JsonResponse(json.dumps(list(matches)), safe=False, status=200)
    return JsonResponse({'error': 'ajax request is required'}, status=400)


class StudentCreateSuccess(BaseAdminView, TemplateView):
    template_name = 'admin/student_create_success.html'


class StudentDeleteView(BaseAdminView, DeleteView):
    model = Student
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('admin-students')

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(self.request, 'You have deleted %s %s successfully'
                         % (student.first_name, student.last_name))
        return super(StudentDeleteView, self).delete(request, *args, **kwargs)


class StudentEditView(BaseAdminView, UpdateView):
    form_class = StudentEditForm
    template_name = 'admin/student_edit.html'
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Student, id=self.kwargs['student_id'])

    def get_success_url(self):
        return reverse_lazy('admin-student-details', kwargs={'student_id': self.object.id})


@login_required
def student_csv_import(request):
    students = request.FILES['students'].read().decode('UTF-8')
    students_textual = io.StringIO(students)
    students_list = list(csv.reader(students_textual, delimiter=','))
    for index in range(len(students_list)):
        stud_info = students_list[index]
        if len(stud_info) == 4:
            correct = True

            if not stud_info[0].replace(' ', '').isalpha() or \
                    not stud_info[1].replace(' ', '').isalpha():
                correct = False
                messages.error(request, 'Student name and surname are invalid, line %d' % index)
            if not stud_info[2].isdigit():
                correct = False
                messages.error(request, 'Student id is invalid, line %d' % index)

            if correct:
                try:
                    Student.objects.create(
                        first_name=stud_info[0],
                        last_name=stud_info[1],
                        id=int(stud_info[2]),
                        speciality=stud_info[3],
                        email=stud_info[2] + '@stu.sdu.edu.kz'
                    )
                except IntegrityError:
                    messages.error(request, 'Student with %s already exists, line %d' % (stud_info[2], index))
        else:
            messages.error(request, 'CSV file structure is incorrect, line %d' % index)

    return HttpResponseRedirect(reverse_lazy('admin-students'))


@login_required
def admin_test(request, user_id, test_id):
    test = get_object_or_404(TestInfo, id=test_id, author=request.user)

    if test.questions.count() == 0:
        question = Question.objects.create(test=test, question='Enter the question', is_multiple_choice=False)
        Option.objects.create(question=question, option='Option 1', is_correct=False)
        Option.objects.create(question=question, option='Option 2', is_correct=False)

    return render(request, 'admin/question_create.html', {'test': test, 'questions': test.questions.all()})


@login_required
def admin_question_add(request, test_id):
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
def admin_question_delete(request, question_id):
    if request.is_ajax() and request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return JsonResponse({'response': 'Question was successfully deleted',
                             'question_id': question_id}, status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)


@login_required
def admin_question_update(request, test_id, question_id):
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
def admin_option_add(request, test_id, question_id):
    if request.is_ajax() and request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        option = Option.objects.create(
            question=question,
            option='Option {}'.format(question.options.count() + 1),
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
