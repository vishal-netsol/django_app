from django.urls import path, include
from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'polls'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', login_required(views.IndexView.as_view()), name='index'),
    # ex: /polls/5/
    # url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    # path('<int:question_id>/', views.detail, name='detail'),
    path('<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
    path('new/', views.NewPollView.as_view(), name="new_poll"),
    path('<int:pk>/delete', views.DeletePoll.as_view(), name="delete_poll"),
    path('<int:pk>/edit', views.EditView.as_view(), name="edit_poll"),
    path('register', views.RegistrationView.as_view(), name="register"),
    path('user_token/', views.UserTokenView.as_view(), name="user_token"),
    path('generate_pdf/', views.GenerateReportView.as_view(), name="generate_pdf"),  
]