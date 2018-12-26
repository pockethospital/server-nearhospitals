from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import reverse

app_name= 'users'

urlpatterns = [
  url(r'^profile/', views.UserProfile.as_view(), name='profile'),
  url(r'^change_password_anonymous/$', views.ChangeUserPasswordAnonymous, name='change-password-anonymous'),
  url(r'^change_password_anonymous_handler/$', views.ChangeUserPasswordAnonymousHandler, name='change-password-anonymous-handler'),
  url(r'^change_user_password/$', views.ChangeUserPassword, name='change-password'),
  url(r'^specialities/$', views.ListSpecialities.as_view(), name='all-specialities'),
  url(r'^get_state/$', views.GetState.as_view(), name='user-location'),
  url(r'^states/$', views.getAllStates, name='all-states'),
  url(r'^state_details/$', views.getState, name='state-details'),
  url(r'^state_cities/$', views.getStateCities, name='state-cities'),
  url(r'^top_cities/$', views.getTopCities, name='top-cities'),
  url(r'^check-user-existance/', views.checkUserExistence, name='check-user-existance'),
  url(r'^login/', views.signin, name='signin'),
  url(r'^register/', views.signup, name='signup'),
  url(r'^logout/', views.signout, name='signout'),
  url(r'^user-otp-verification/', views.userOTPVerification, name='user-otp-verification'),
  url(r'^user-otp-validation/', views.userOTPValidation, name='user-otp-validation'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
