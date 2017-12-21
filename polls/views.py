from django.shortcuts import get_object_or_404, render
from .models import Question, Choice
from django.views import generic
from .forms import PollForm, AnswerForm, SignUpForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
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
        return self.request.GET.get('redirect_to', '/polls')

@method_decorator(login_required, name='dispatch')
class DeletePoll(generic.DeleteView):
    model = Question
    success_url = '/polls'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class EditView(generic.UpdateView):
    model = Question
    form_class = PollForm
    template_name = 'polls/new.html'
    success_url = '/polls'

    def form_valid(self, form):
        form.save()
        return super(EditView, self).form_valid(form)


class RegistrationView(generic.FormView):
    form_class = SignUpForm
    model = User
    template_name = 'registrations/new.html'
    success_url = '/polls'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        import pdb; pdb.set_trace()
        user.save()
        current_site = get_current_site(self.request)
        subject = 'Activate your blog account.'
        text_content = 'Account Activation Email'

        template_name = "registrations/activation_mail.html"
        recipients = form.cleaned_data.get('email')
        kwargs = {
            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            "token": default_token_generator.make_token(user)
        }
        activation_url = reverse("activate", kwargs=kwargs)

        activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)

        context = {
            'user': user,
            'activate_url': activate_url
        }
        html_content = render_to_string(template_name, context)
        email = EmailMessage(subject, text_content,to=recipients)
        email.attach_alternative(html_content, "text/html")
        email.send()

        return super(RegistrationView, self).form_valid(form)

class AccountActivationView(generic.RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        import pdb; pdb.set_trace()
        return super().get_redirect_url(*args, **kwargs)