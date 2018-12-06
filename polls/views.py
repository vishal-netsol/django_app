import requests
import json
from django.shortcuts import get_object_or_404, render
from .models import Question, Choice
from django.views import generic
from .forms import PollForm, AnswerForm, SignUpForm, AuthenticationForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from accounts.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# from django.http import HttpResponseRedirect
# from django.urls import reverse

# Create your views here.
# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')

@method_decorator(login_required, name='dispatch')
class DetailView(generic.FormView):
    model = Choice
    form_class = AnswerForm
    template_name = 'polls/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['question'] = Question.objects.filter(pk=self.kwargs['pk']).first()
        return context

    def form_valid(self, form):
        choice = form.save(commit=False)
        choice.question_id = self.kwargs['pk']
        choice.save()
        return super(DetailView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy( 'polls:detail', kwargs={'pk': self.kwargs['pk']})

@method_decorator(login_required, name='dispatch')
class NewPollView(generic.FormView):
    model = Question
    form_class = PollForm
    template_name = 'polls/new.html'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.pub_date = timezone.now()
        question.save()
        return super(NewPollView, self).form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('redirect_to', '/polls/')

@method_decorator(login_required, name='dispatch')
class DeletePoll(generic.DeleteView):
    model = Question
    success_url = '/polls/'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class EditView(generic.UpdateView):
    model = Question
    form_class = PollForm
    template_name = 'polls/new.html'
    success_url = '/polls/'

    def form_valid(self, form):
        form.save()
        return super(EditView, self).form_valid(form)


class RegistrationView(generic.FormView):
    form_class = SignUpForm
    model = User
    template_name = 'registrations/new.html'
    success_url = '/accounts/login/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        # current_site = get_current_site(self.request)
        # mail_subject = 'Activate your blog account.'
        # message = render_to_string('registrations/activation_mail.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        #     'token': account_activation_token.make_token(user),
        # })
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage(
        #             mail_subject, message, to=[to_email]
        # )
        # email.send()

        return super(RegistrationView, self).form_valid(form)

class SessionView(generic.FormView):
    form_class = AuthenticationForm
    model = User
    template_name = 'sessions/new.html'
    success_url = '/polls/'

    def form_valid(self, form):
        user = form.get_user()      
        auth_login(self.request, user)
        return super(SessionView, self).form_valid(form)

class AccountActivationView(generic.RedirectView):
    
    def get(self, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, kwargs['token']):
            user.is_active = True
            user.save()
            auth_login(self.request, user)
            return super(AccountActivationView,self).get(*args, **kwargs)
        else:
            return HttpResponse('Activation link is invalid!')
    
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get('redirect_to', '/polls/')

class NotFoundView(generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get('redirect_to', '/polls/')

class UserTokenView(generic.View):

    def get(self, request, *args, **kwargs):
        try:
            code = self.request.GET.get('code')
            url = "http://localhost:3000/openid/token/"
            data = {"client_id": '135261', "client_secret": '74982081b7f2a6fe08341fbeb4792bc6d4aeae056bdcc5fb80265bc8', "grant_type": "authorization_code", "code": code, "redirect_uri": "http://localhost:3001/polls/user_token/"}
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control': 'no-cache'}
            response = requests.post(url, data=data, headers=headers)
            access_token = json.loads(response.content.decode('utf-8'))['access_token']
            headers = {'Cache-Control': 'no-cache'}
            url = 'http://localhost:3000/openid/userinfo/?access_token='+access_token
            response = requests.get(url, headers=headers)
            email = json.loads(response.content.decode('utf-8'))['email']
            user = User.objects.filter(email=email).first()
            auth_login(self.request, user)
            return HttpResponseRedirect('/polls/')
        except:
            return JsonResponse({"message": "Record doesn't exist"})