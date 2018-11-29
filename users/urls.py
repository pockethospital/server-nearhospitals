from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

app_name= 'users'

urlpatterns = [
  url(r'^login/', views.login, name='login'),
  # url(r'^login/', views.login, name='login'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
