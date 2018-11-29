from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from annoying.functions import get_object_or_None
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from django.core import serializers
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer, json
from django.utils import timezone
from datetime import timedelta, date, datetime
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import Permission, User
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from .models import Users, Favorite, Visit, PaymentTransaction, Appointment, Help, History, SavedCard, Wallet, MedicalRecordUpload, MedicalRecord, Reminder
from django.contrib.contenttypes.models import ContentType
import re
import googlemaps

# Create your views here.

#Perform User Login and Signup
@api_view(["POST"])
def login(request):
  username = request.data.get("username")
  password = request.data.get("password")
  user = authenticate(username=username, password=password)
  if not user:
    print(get_object_or_None(User, username= username))
    if get_object_or_None(User, username= username) is not None:
      return Response({ "error": "Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED )
    else:
      return Response({ "error": "Come here for Signup"}, status=status.HTTP_401_UNAUTHORIZED )
  else:
    return Response({"error": "Login Successful"}, status=status.HTTP_200_OK)
    # else:
    #   user = User.objects.create_user(username=username, email=None, password=password)
    #   user.is_active = False
    #   user.save()
    #   Users.objects.get_or_create(user=user)