from django import forms

from .models import Question, Choice
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from accounts.models import User


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254)
    username = forms.CharField(max_length=30, required=False, help_text='Optional.')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email' )

class PollForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('question_text',)

class AnswerForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = ('choice_text',)

class AuthenticationForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required.')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Invalid credentails",
    }

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user = User._default_manager.get(email__iexact=email)
                import pdb; pdb.set_trace()
                if user.check_password(password):
                    self.form_user = user
            except User.DoesNotExist:
                self.form_user = None
            if self.form_user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': email},
                )
        return self.cleaned_data

    def get_user(self):
        return self.form_user
