import csv
import io
import json
from string import ascii_lowercase

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
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, RedirectView

from things.admin_forms.forms import (
    UserCreateForm, UserAuthForm, TestCreateForm, StudentCreateForm, StudentEditForm,
    StudentTestAddForm
)
from things.models import TestInfo, Question, Option, User, Student, TestResult, Speciality
from things.utils.tasks import send_mail_wrapper
from things.utils.activation_token import activation_token
from things.utils.utils import lower_headers, Round


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
        return reverse_lazy('admin-tests')

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
        return reverse_lazy('admin-home')


def initial(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin-home'))
    else:
        return HttpResponseRedirect(reverse('admin-login'))


class LogoutView(BaseLogoutView):
    def get_next_page(self):
        return reverse_lazy('admin-login')


class BaseAdminView(LoginRequiredMixin):
    pass


class HomeView(BaseAdminView, DetailView):
    model = User
    template_name = 'admin/home.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students_number'] = Student.objects.all().count()
        return context


class AdminTestCreateView(BaseAdminView, CreateView):
    model = TestInfo
    form_class = TestCreateForm
    template_name = 'admin/test_create.html'

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        encoded_id = urlsafe_base64_encode(force_bytes(self.object.id))
        domain = get_current_site(self.request)
        url = reverse('admin-filter-students', kwargs={'uidb64': encoded_id})
        self.object.link = 'http://{}{}'.format(domain, url)

        self.request.session['test_id'] = self.object.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('admin-test', kwargs={'test_id': self.object.id})


class AdminTestUpdateView(BaseAdminView, UpdateView):
    model = TestInfo
    form_class = TestCreateForm
    template_name = 'admin/test_update.html'
    context_object_name = 'test'

    def get(self, request, *args, **kwargs):
        if not request.session.get('test_id') \
                or request.session.get('test_id') != self.get_object().id:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(TestInfo, author=self.request.user,
                                 id=self.kwargs['test_id'])

    def get_success_url(self):
        if self.request.POST.get('destination'):
            return self.request.POST.get('destination')
        else:
            return reverse_lazy('admin-test', kwargs={'test_id': self.get_object().id})


class BaseGroupsView(BaseAdminView, FormView):
    form_class = StudentTestAddForm

    def get_object(self):
        return get_object_or_404(TestInfo, author=self.request.user,
                                 id=self.kwargs['test_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = self.get_object()
        context['test'] = test
        context['checked'] = list(test.students.all().values_list('speciality', flat=True).distinct())
        return context

    def form_valid(self, form):
        test = self.get_context_data()['test']
        specialities = set(form.cleaned_data['specialities'].values_list('id', flat=True))
        initial_specialities = set(self.get_context_data()['checked'])

        if initial_specialities.issubset(specialities):
            new_specialities = specialities.difference(initial_specialities)
            students = Student.objects.filter(speciality__in=new_specialities)
            test.students.add(*students)
        elif initial_specialities.issuperset(specialities):
            new_specialities = initial_specialities.difference(specialities)
            students = Student.objects.filter(speciality__in=new_specialities)
            test.students.remove(*students)
        else:
            remaining = initial_specialities.intersection(specialities)
            if remaining:
                toremove = initial_specialities.difference(specialities)
                students = Student.objects.filter(speciality__in=toremove)
                test.students.remove(*students)
                toadd = specialities.difference(initial_specialities)
                students = Student.objects.filter(speciality__in=toadd)
                test.students.add(*students)
            else:
                students = Student.objects.filter(speciality__in=specialities)
                test.students.clear()
                test.students.add(*students)

        return HttpResponseRedirect(self.get_success_url())


class TestStudentAddView(BaseGroupsView):
    template_name = 'admin/test_add_student.html'

    def get(self, request, *args, **kwargs):
        if not request.session.get('test_id') \
                or request.session.get('test_id') != self.get_context_data()['test'].id:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.POST.get('destination'):
            return self.request.POST.get('destination')
        else:
            del self.request.session['test_id']
            test_id = self.get_context_data()['test'].id
            return reverse_lazy('admin-share-test', kwargs={'test_id': test_id})


@login_required
def share_test(request, test_id):
    test = get_object_or_404(TestInfo, author=request.user,
                             id=test_id)
    return render(request, 'admin/test_invite.html', {'link': test.link})


def filter_students(request, uidb64):
    test = None
    try:
        test_id = force_text(urlsafe_base64_decode(uidb64))
        test = TestInfo.objects.get(id=test_id)
        correct = True
    except (TypeError, ValueError, OverflowError, TestInfo.DoesNotExist, ValidationError):
        correct = False

    if correct and test.is_active == TestInfo.TestState.ongoing:
        # TODO change redirect url
        return HttpResponse(content=uidb64)
    else:
        # TODO change redirect url
        messages.error(request, 'Test link is invalid')
        return HttpResponseRedirect(reverse('admin-login'))


class AdminTestListView(BaseAdminView, ListView):
    model = TestInfo
    context_object_name = 'tests'
    template_name = 'admin/tests.html'
    paginate_by = 4

    def get_queryset(self):
        try:
            title = self.request.GET['title']
        except KeyError:
            title = None

        if title is not None:
            queryset = self.request.user.tests.filter(title__contains=title)
        else:
            queryset = self.request.user.tests

        return queryset \
            .order_by('-created_date') \
            .annotate(average_points=Round(Avg('results__grade'), 2))

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
        context['test_state'] = TestInfo.TestState.__members__
        return context

    def get_queryset(self):
        return self.request.user.tests.all()


class TestEditView(BaseAdminView, UpdateView):
    form_class = TestCreateForm
    template_name = 'admin/test_edit.html'
    context_object_name = 'test'
    pk_url_kwarg = 'test_id'

    def get(self, request, *args, **kwargs):
        test = self.get_object()
        if test.is_active == TestInfo.TestState.ongoing or test.is_active == TestInfo.TestState.finished:
            return HttpResponse(content="You can't edit this test", status=409)
        self.request.session['edited_test_id'] = test.id
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(TestInfo, author=self.request.user,
                                 id=self.kwargs['test_id'])

    def get_success_url(self):
        if self.request.POST.get('destination'):
            return self.request.POST.get('destination')
        else:
            return reverse_lazy('admin-edit-questions', kwargs={'test_id': self.object.id})


@login_required
def admin_test_edit(request, test_id):
    if not request.session.get('edited_test_id') \
            or request.session.get('edited_test_id') != test_id:
        raise Http404

    test = get_object_or_404(TestInfo, id=test_id, author=request.user)

    if request.method == 'GET':
        if test.is_active == TestInfo.TestState.ongoing or test.is_active == TestInfo.TestState.finished:
            return HttpResponse(content="You can't edit this test", status=409)

    return render(request, 'admin/question_edit.html', {'test': test, 'questions': test.questions.all()})


class TestEditStudentsView(BaseGroupsView):
    template_name = 'admin/test_student_edit.html'

    def get(self, request, *args, **kwargs):
        test = self.get_object()
        if test.is_active == TestInfo.TestState.ongoing or test.is_active == TestInfo.TestState.finished:
            return HttpResponse(content="You can't edit this test", status=409)
        if not request.session.get('edited_test_id') \
                or request.session.get('edited_test_id') != self.get_context_data()['test'].id:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.POST.get('destination'):
            return self.request.POST.get('destination')
        else:
            del self.request.session['edited_test_id']
            return reverse_lazy('admin-test-details', kwargs={'test_id': self.get_object().id})


class TestDeleteView(BaseAdminView, DeleteView):
    model = TestInfo
    pk_url_kwarg = 'test_id'

    def get_queryset(self):
        return self.request.user.tests.all()

    def get_success_url(self):
        return reverse_lazy('admin-tests')

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        messages.success(self.request, 'You have deleted %s test successfully'
                         % test.title)
        return super(TestDeleteView, self).delete(request, *args, **kwargs)


@login_required
def copy_test(request, test_id):
    test = get_object_or_404(TestInfo, author=request.user,
                             id=test_id)
    copy = test.clone()
    encoded_id = urlsafe_base64_encode(force_bytes(copy.id))
    domain = get_current_site(request)
    url = reverse('admin-filter-students', kwargs={'uidb64': encoded_id})
    copy.link = 'http://{}{}'.format(domain, url)
    copy.save()
    request.session['test_id'] = copy.id
    return HttpResponseRedirect(reverse_lazy('admin-update-test', kwargs={'test_id': copy.id}))


@login_required
def students_results(request, test_id, sort_by):
    if request.is_ajax() and request.method == 'POST':
        test = get_object_or_404(TestInfo, author=request.user.id,
                                 id=test_id)
        results = test.students.all() \
            .annotate(points=F('results__grade')) \
            .annotate(result_id=F('results__id')) \
            .annotate(speciality_title=F('speciality__title'))
        if sort_by == 'student-name':
            results = results.order_by('first_name', 'last_name')
        elif sort_by == 'student-group':
            results = results.order_by('speciality__title')
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
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        if request.session.get('stud_create_flag'):
            del request.session['stud_create_flag']
        elif request.session.get('stud_import_flag'):
            del request.session['stud_import_flag']
        return super().get(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def colors(self):
        return [('#FFD058', '#F2AE00'),
                ('#EF6363', '#EF6363'),
                ('#3BD277', '#119A48')]

    def get_queryset(self):
        try:
            name = self.request.GET['student']
            if ' ' in name:
                name = name.split(' ')
        except KeyError:
            name = None

        if name is not None and isinstance(name, list) and len(name) == 2:
            queryset = Student.objects.filter(
                Q(first_name__startswith=name[0]) | Q(last_name__startswith=name[1])
                | Q(first_name__startswith=name[1]) | Q(last_name__startswith=name[0]))
        elif name is not None and isinstance(name, str):
            queryset = Student.objects.filter(
                Q(first_name__startswith=name) | Q(last_name__startswith=name))
        else:
            queryset = Student.objects.all()

        return queryset \
            .order_by('-created_date')


class StudentDetailView(BaseAdminView, DetailView):
    model = Student
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    template_name = 'admin/student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = self.object.tests.all().annotate(point=F('results__grade')) \
            .annotate(question_rate=Count('results__answers', filter=Q(results__answers__answer__is_correct=True)))
        context['test_state'] = TestInfo.TestState.__members__
        return context

    def get_queryset(self):
        return Student.objects.all()


class StudentCreateView(BaseAdminView, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = 'admin/student_create.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('stud_create_flag'):
            del request.session['stud_create_flag']
        elif request.session.get('stud_import_flag'):
            del request.session['stud_import_flag']

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # noinspection PyAttributeOutsideInit
        self.request.session['stud_create_flag'] = True
        return super().form_valid(form)

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

    def get(self, request, *args, **kwargs):
        if not request.session.get('stud_create_flag'):
            raise Http404
        return super().get(request, *args, **kwargs)


class StudentDeleteView(BaseAdminView, DeleteView):
    model = Student
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('admin-students')

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(self.request, 'You have deleted %s %s successfully'
                         % (student.last_name, student.first_name))
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
    outof = 0
    for index in range(len(students_list)):
        stud_info = students_list[index]
        if len(stud_info) == 4:
            correct = True

            if not stud_info[0].replace(' ', '').isalpha() or \
                    not stud_info[1].replace(' ', '').isalpha():
                outof += 1
                continue
            if not stud_info[2].isdigit():
                outof += 1
                continue
            if not stud_info[3]:
                outof += 1
                continue

            if correct:
                try:
                    speciality = Speciality.objects.get_or_create(
                        title=stud_info[3].strip().upper())[0]
                    Student.objects.create(
                        first_name=stud_info[0],
                        last_name=stud_info[1],
                        id=int(stud_info[2]),
                        speciality=speciality,
                        email=stud_info[2] + '@stu.sdu.edu.kz'
                    )
                except IntegrityError:
                    outof += 1
        else:
            outof += 1

    totalrow = len(students_list)
    del request.session['totalrow']
    del request.session['successrow']
    request.session['stud_import_flag'] = True
    request.session['totalrow'] = totalrow
    request.session['successrow'] = totalrow - outof

    return HttpResponseRedirect(reverse_lazy('admin-csv-message-view'))


class CsvImportMessageView(BaseAdminView, TemplateView):
    template_name = 'admin/csv_import_message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.session.get('stud_import_flag'):
            raise Http404

        try:
            context['totalrow'] = self.request.session['totalrow']
            context['successrow'] = self.request.session['successrow']
        except KeyError:
            raise Http404

        return context


@login_required
def admin_test(request, test_id):
    if not request.session.get('test_id') or request.session.get('test_id') != test_id:
        raise Http404

    test = get_object_or_404(TestInfo, id=test_id, author=request.user)

    return render(request, 'admin/question_create.html', {'test': test, 'questions': test.questions.all()})


@login_required
def questions_csv_import(request, test_id):
    if not request.session.get('test_id') or request.session.get('test_id') != test_id:
        raise Http404

    test = get_object_or_404(TestInfo, author=request.user,
                             id=test_id)
    file = request.FILES['questions'].read().decode('UTF-8')
    csv_str = io.StringIO(file)
    questions = csv.DictReader(lower_headers(csv_str), delimiter=',', quotechar='"')
    totalrow, outof = 0, 0
    for row in questions:
        totalrow += 1
        correct_num = 0
        try:
            question = Question.objects.create(
                test=test,
                question=row['question']
            )
            correct = [c.strip().lower() for c in row['correct'].split(',')]
            for letter in ascii_lowercase:
                if letter in questions.fieldnames \
                        and row[letter] is not None:
                    option = Option.objects.create(
                        question=question,
                        option=row[letter],
                        is_correct=letter in correct
                    )

                    if option.is_correct:
                        correct_num += 1

            if correct_num > 1:
                question.is_multiple_choice = True
        except KeyError:
            outof += 1

    messages.info(request, '%d questions were created successfully out of %d' % (totalrow - outof, totalrow))

    return HttpResponseRedirect(reverse_lazy('admin-test', kwargs={'test_id': test_id}))


@login_required
def admin_question_delete(request, question_id):
    if request.is_ajax() and request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return JsonResponse({'response': 'Question was successfully deleted',
                             'question_id': question_id}, status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)


@login_required
def admin_question_update(request):
    if request.is_ajax() and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question = Question.objects.get(id=data['id'])
        question.question = data['question']
        question.is_multiple_choice = data['is_multiple_choice']
        question.save()

        options = list()
        for opt in data['options']:
            if 'id' in opt:
                option = Option.objects.get(id=opt['id'])
                option.option = opt['option']
                option.is_correct = opt['is_correct']
                option.save()
            else:
                option = Option.objects.create(
                    option=opt['option'],
                    is_correct=opt['is_correct'],
                    question=question
                )
            options.append({
                'id': option.id, 'option': option.option, 'is_correct': option.is_correct
            })

        response = {'id': question.id, 'question': question.question,
                    'is_multiple_choice': question.is_multiple_choice, 'options': options}

        return JsonResponse(json.dumps(response), status=200, safe=False)

    return JsonResponse({'error': 'ajax request is required'}, status=400)


@login_required
def ajax_question_create(request):
    if request.is_ajax() and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        test = get_object_or_404(TestInfo, author=request.user,
                                 id=data['test_id'])
        question = Question.objects.create(
            question=data['question'],
            is_multiple_choice=data['is_multiple_choice'],
            test=test
        )

        options = list()
        for option in data['options']:
            obj = Option.objects.create(
                question=question,
                option=option['option'],
                is_correct=option['is_correct']
            )
            options.append({
                'id': obj.id, 'option': obj.option, 'is_correct': obj.is_correct
            })

        response = {'id': question.id, 'question': question.question,
                    'is_multiple_choice': question.is_multiple_choice, 'options': options}

        return JsonResponse(json.dumps(response),
                            safe=False,
                            status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)
