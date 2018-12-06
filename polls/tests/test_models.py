from django.test import TestCase
from django.utils import timezone
from polls.models import Question

class QuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Question.objects.create(question_text="what's your rashee?", pub_date = timezone.now())

    def test_question_label(self):
        question = Question.objects.get(id=1)
        field_label = question._meta.get_field('question_text').verbose_name
        self.assertEquals(field_label, 'question text')
    
    def test_pub_date_label(self):
        question = Question.objects.get(id=1)
        field_label = question._meta.get_field('pub_date').verbose_name
        self.assertEquals(field_label, 'date published')
    
    def test_object_name_is_question_text(self):
        question = Question.objects.get(id=1)
        expected_object_name = question.question_text
        self.assertEquals(expected_object_name, str(question))