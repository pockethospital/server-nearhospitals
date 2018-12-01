from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

app_name= 'users'

urlpatterns = [
  url(r'^profile/', views.UserProfile.as_view(), name='profile'),
  url(r'^change_password_anonymous/$', views.ChangeUserPasswordAnonymous),
  url(r'^change_password_anonymous_handler/$', views.ChangeUserPasswordAnonymousHandler),
  url(r'^change_user_password/$', views.ChangeUserPassword),
  url(r'^specialities/$', views.ListSpecialities.as_view()),
  url(r'^get_state/$', views.GetState.as_view()),
  url(r'^login/', views.signin, name='signin'),
  url(r'^signup/', views.signup, name='signup'),
  url(r'^logout/', views.signout, name='signout'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
