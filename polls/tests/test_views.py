from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from polls.models import Question

class QuestionListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User(email="v@s.com")
        user.set_password('password')
        user.save()
        number_of_questions = 4

        for ques_id in range(number_of_questions):
            Question.objects.create(question_text='Question '+str(ques_id + 1), pub_date=timezone.now() )
    
    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(email='v@s.com', password='password')
        response = self.client.get('/polls/')
        self.assertEqual(response.status_code, 200)
    
    def test_question_objects(self):
        login = self.client.login(email='v@s.com', password='password')
        response = self.client.get('/polls/')
        self.assertEqual(response.context['object_list'].count(), 4)