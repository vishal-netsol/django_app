"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from polls import views as poll_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('polls/', include('polls.urls')),
    url(r'^accounts/login/$', poll_views.SessionView.as_view(), name="signin"),
    url(r'^logout/$', auth_views.logout, {'next_page': 'http://localhost:3000/user/login/'}),
    url(r'^register/$', poll_views.RegistrationView.as_view(), name='signup'),
    url(r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        poll_views.AccountActivationView.as_view(), name='activate'),
    url(r'^.*$', poll_views.NotFoundView.as_view(), name='not_found'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
