from django.test import TestCase
from accounts.models import User
from polls.forms import PollForm, SignUpForm, AuthenticationForm

class PollFormTest(TestCase):

    def test_poll_form_question_field_label(self):
        form = PollForm()
        self.assertTrue(form.fields['question_text'].label == None or form.fields['question_text'].label == 'Question text')

class SignUpFormTest(TestCase):

    def test_sign_up_form_first_name_field_label(self):
        form = SignUpForm()
        self.assertTrue(form.fields['first_name'].label == None or form.fields['first_name'].label == 'First Name')
    
    def test_sign_up_form_first_name_field_validation(self):
        form = SignUpForm()
        self.assertTrue(form.fields['first_name'].required)

class AuthenticationFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = User(email="v@s.com")
        user.set_password('password')
        user.save()

    # Valid Form Data
    def test_UserForm_valid(self):
        form = AuthenticationForm(data={'email': "v@s.com", 'password': "password"})
        self.assertTrue(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = AuthenticationForm(data={'email': "", 'password': "mp"})
        self.assertFalse(form.is_valid())

class SignUpFormTest(TestCase):

    # Valid Form Data
    def test_UserForm_valid(self):
        form = AuthenticationForm(data={'email': "v@s.com", 'password': "password"})
        self.assertTrue(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = AuthenticationForm(data={'email': "", 'password': "mp"})
        self.assertFalse(form.is_valid())
