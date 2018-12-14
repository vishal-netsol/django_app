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
            data = {"client_id": '747149', "client_secret": '68de1bbee1fd5c8db64a34583886451b1c57d1f75b90e7ef9ca8a3c0', "grant_type": "authorization_code", "code": code, "redirect_uri": "http://localhost:3001/polls/user_token/"}
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control': 'no-cache'}
            response = requests.post(url, data=data, headers=headers)
            access_token = json.loads(response.content.decode('utf-8'))['access_token']
            headers = {'Cache-Control': 'no-cache'}
            request.session['access_token'] = access_token
            url = 'http://localhost:3000/openid/userinfo/?access_token='+access_token
            response = requests.get(url, headers=headers)
            username = json.loads(response.content.decode('utf-8'))['preferred_username']
            user = User.objects.filter(username=username).first()
            auth_login(self.request, user)
            return HttpResponseRedirect('/polls/')
        except:
            return JsonResponse({"message": "Record doesn't exist"})


class GenerateReportView(generic.View):

    def get(self, *args, **kwargs):
        url = "http://localhost:3002/reports/"
        data = '{"application":"747149","template":"skolplattformen-theme","document":[{"title":"My custom report","created_at":"2018-10-25 08:04:06","created_by":"Christian Wannerstedt","header":{"logo":{"url":"https://s3.eu-central-1.amazonaws.com/url-to-skolplattformen-logo.png","width":100,"height":30,"content-type":"image/jpg"},"text":"School name"},"footer":{"text":"Username, 2018-10-26","pagination":true},"components":[{"type": "container", "page-break": "true", "components": [{"type": "title", "title": "Anm\u00e4lan till rektor"}]}, {"type": "container", "components": [{"type": "title", "title": "Vad g\u00e4ller anm\u00e4lan"}, {"text": "Upplevd diskriminering/kr\u00e4nkning", "type": "paragraph", "page-break": "true"}]}, {"type": "container", "components": [{"type": "title", "title": "Beskriv orsaken till anm\u00e4lan"}, {"text": "Efter tjafs mellan flera elever och Leon i 6b tar Valle n\u00e5gon/n\u00e5gra elever i f\u00f6rsvar. Leon tar d\u00e4refter ett grepp med h\u00e4nderna om huvudet p\u00e5 Valle och vrider om s\u00e5 det knakar. Inga men efter\u00e5t kan konstateras, men Valle blev r\u00e4dd och k\u00e4nde sig otrygg. En obehaglig situation. Valles \u00e4ldre syster Lova tar senare lillebror i f\u00f6rsvar och hotar Leon med stryk och jagar honom. Inget fysiskt br\u00e5k uppst\u00e5r dock. Lova k\u00e4nner sig senare utpekad av Leons klasskamrater.\n\nDet allvarliga h\u00e4r dock, att Leon vridit huvet p\u00e5 Valle.", "type": "paragraph"}]}, {"type": "container", "components": [{"type": "title", "title": "Arbetslagets syn p\u00e5 situationen"}, {"text": "Mentor, skolledning  och elevh\u00e4lsan informerades direkt efter h\u00e4ndelsen.", "type": "paragraph"}]}, {"type": "container", "components": [{"type": "title", "title": "Elevens och elevens v\u00e5rdnadshavares syn p\u00e5 situationen"}, {"text": "Valles f\u00f6r\u00e4ldrar f\u00e5r k\u00e4nnedom om det intr\u00e4ffade av skolan samma dag 2018-08-31. F\u00f6r\u00e4ldrarna \u00e4r med all r\u00e4tt uppr\u00f6rda. ", "type": "paragraph"}]}, {"type": "container", "components": [{"type": "title", "title": "Beskriv vilka \u00e5tg\u00e4rder som redan vidtagits"}, {"text": "Eftersom Leon uppvisat ett d\u00e5ligt beteende ett stort antal g\u00e5nger f\u00f6rut, varit upphov till m\u00e5nga konflikter och br\u00e5k, beslutar skolledningen om att skriftlig varning skall utdelas. Detta sker samma dag p\u00e5 kv\u00e4llen, 2018-08-31 (fredag).\n\nSkolan f\u00f6ljer upp med telefonsamtal till VH p\u00e5 m\u00e5ndag morgon , 2018-09-03. I samtalet beslutades att VH kommer till skolan f\u00f6r m\u00f6te s\u00e5 snart skolsk\u00f6terskan \u00e4r tillbaks fr\u00e5n ledighet. F\u00f6rsta m\u00f6jliga dag f\u00f6r m\u00f6te: 11/9. Skolsk\u00f6terskan kallar till m\u00f6tet som ocks\u00e5 omfattar mentor. En omfattade handlingsplan f\u00f6resl\u00e5s.", "type": "paragraph"}]}, {"type": "container", "components": [{"type": "title", "title": "Eventuella f\u00f6rslag p\u00e5 hur \u00e4rendet kan utredas"}, {"text": "F\u00f6rslag p\u00e5 \u00e5tg\u00e4rd: Dagliga avst\u00e4mningssamtal med skolsk\u00f6terska innan Leon g\u00e5r hem (tis, och och tors) varje vecka under l\u00e4ngre tid. Skolledningen \u00f6verl\u00e5ter till Elevh\u00e4lsan att ta fram en handlingsplan som f\u00f6rankras av elev, VH och l\u00e4rare.", "type": "paragraph"}, {"type": "customstyle", "style": "margin-top: 150px; margin-left: 150px;", "html": "<p style=color:red;>Any <b>custom</b> html goes here</p>" }, {"type": "image", "avoid_page_break": true, "src": "https://gopbj.com/assets/second-block-photo-1.jpg", "width": 300, "height": 300} ]}]}]}'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.request.session['access_token']}
        response = requests.post(url, data=data, headers=headers)
        return HttpResponseRedirect('/polls')

class LogoutView(generic.View):

    def get(self, request, *args, **kwargs):
        url = "http://localhost:3000/user/logout/?access_token=%s" % self.request.session['access_token']
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.request.session['access_token']}
        response = requests.get(url, headers=headers)
        auth_logout(request)
        return HttpResponseRedirect('/polls')