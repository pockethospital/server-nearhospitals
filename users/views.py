from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from annoying.functions import get_object_or_None
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import JSONRenderer, json
from django.utils import timezone
from datetime import timedelta, date, datetime
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import Permission, User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import send_mail
# from .models import Users, Favorite, Visit, PaymentTransaction, Appointment, Help, History, SavedCard, Wallet, MedicalRecordUpload, MedicalRecord, Reminder
from . import models
from django.contrib.contenttypes.models import ContentType
import re
import googlemaps
from nearhospitals.libs.validations import checkExistence
from django.views.decorators.csrf import csrf_exempt
from . import serializers

# Create your views here.

# If you want to make the data request from the same domain of the server. 

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
  username = request.data.get("username")
  password = request.data.get("password")
  user = authenticate(username=username, password=password)
  if not user:
    if get_object_or_None(User, username= username) is not None:
      return Response({ "statusMessage": "Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED )
    else:
      return Response({ "statusMessage": "Come here for Signup"}, status=status.HTTP_202_ACCEPTED )
  else:
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
      {
        "statusMessage": "Login Successful",
        "fullName": user.fullName(),
        "token": token.key
      }, status=status.HTTP_200_OK)

@api_view(["POST"])
def signout(request):
  return Response(
    {
      "token": None,
      "username": None,
      "statusMessage": "Successfully Logged Out"
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
  username = request.data.get("username")
  password = request.data.get("password")
  confirmPassword = request.data.get("confirmPassword")
  
  if get_object_or_None(User, username= username) is not None:
    return Response({"statusMessage": "User Already Exists. Please Login or Recover Password if your forget it."}, status=status.HTTP_400_BAD_REQUEST)

  if checkExistence(username) and checkExistence(password) and checkExistence(confirmPassword):
    if password != confirmPassword:
      return Response({"statusMessage": "Passwords doesn't matched"}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
      return Response({"statusMessage": "Passwords length must be minimum of 5"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username="user-"+username, email=None, password=password)
    user.is_active = True
    token = Token.objects.create(user=user)
    models.Users.objects.get_or_create(user=user, mobile=username, slug=token.key)
    user.save()
    return Response(
      {
        "statusMessage": "Signup Successful",
        "username": user.username
      }, status=status.HTTP_200_OK)
  else:
    return Response({"statusMessage": "Inputs are missing"}, status=status.HTTP_400_BAD_REQUEST)

# Change Password with username only i.e., Mobile Number
@api_view(["POST"])
def ChangeUserPasswordAnonymousHandler(request):
  user = get_object_or_None(User, username=request.data.get("username"))
  if user is not None:
    print(user.password)
    if user.password == request.data.get("hasher"):
      if request.data.get("new_password") is not None:
        newPassword = make_password(password=request.data.get("new_password")) 
        print(newPassword)
        user.password = newPassword
        user.save()
        return Response({
          "success": "Password has been changed successfully"
        })
      else:
        return Response({ "error": "New Password is missing" }, status= status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({ "error": "Password is already changed. Invalid Link" }, status= status.HTTP_401_UNAUTHORIZED)
  else:
    return Response({ "error": "Invalid username" }, status= status.HTTP_401_UNAUTHORIZED)

#Change the User AUthenticatin Password With Email Id
@api_view(["POST"])
def ChangeUserPasswordAnonymous(request):
  emailRegex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
  usernameRegex = r'^[A-Za-z]+[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$'
  phoneRegex = r'^[0-9]{5,}$'
  
  print( re.match(usernameRegex, request.data.get("cred")))

  if re.match(emailRegex, request.data.get("cred"), flags=0) is not None:
    user = get_object_or_None(User, email=request.data.get("cred"))
    if user is None:
      return Response({"error": "Invalid Email ID"}, status= status.HTTP_401_UNAUTHORIZED)
  elif re.match(usernameRegex, request.data.get("cred"), flags=0) is not None:
    user = get_object_or_None(User, username=request.data.get("cred"))
    if user is None:
      return Response({ "error": "Invalid Username"}, status= status.HTTP_401_UNAUTHORIZED )
  elif re.match(phoneRegex, request.data.get("cred"), flags=0) is not None:
    users = get_object_or_None(Users, mobile=request.data.get("cred"))
    if users is not None:
      user = users.user
    else:
      return Response({ "error": "Invalid Phone Number" }, status= status.HTTP_401_UNAUTHORIZED )
  else:
    return Response({ "error": "Invalid Credential. Check Your Input" }, status= status.HTTP_401_UNAUTHORIZED)

  subject = "Pocket Hospital's User Password Recovery Mail."
  message = "<a href='http://localhost:8080/forget_password/"+ user.username +"/"+ user.password +"/'>Click Here to Change Password</a>"
  sender = "Pocket Hospital"

  to = user.email
  if len(to):
    if send_mail(subject, message, sender, [to], fail_silently=False):
      return Response({
        "success": "Mail sent to the registered email Id"
      })
    else:
      return Response({ "error": "Techincal Issue Can't send mail. Contact at technical@pockethospital.com" }, status= status.HTTP_401_UNAUTHORIZED)
  else:
      return Response({ "error": "No Email Id is Registered with us. Contact at technical@pockethospital.com" }, status= status.HTTP_401_UNAUTHORIZED)


# Change the User AUthenticatin Password With Old Password 
@api_view(["PUT"])
def ChangeUserPassword(request):
  user = get_object_or_None(User, username=request.data.get("username"))
  if not user:
      return Response({ "error": "Invalid Username"}, status= status.HTTP_401_UNAUTHORIZED )
  else:
    print(user.password)
    if check_password(password=request.data.get("old_password"), encoded=user.password):
      newPassword = make_password(password=request.data.get("new_password")) 
      print(newPassword)
      user.password = newPassword
      user.save()
      return Response({
        "success": "Password Has Been Changed Successfully"
      })
    else:
      return Response({ "error": "Invalid Old Password"}, status= status.HTTP_401_UNAUTHORIZED )



# User Profile Classes
class UserProfile(generics.RetrieveAPIView):
  serializer_class = serializers.UsersSerializer
  queryset = models.Users.objects.all()
  permission_classes = ""


class GetState(APIView):
  cities = []
  states = []
  userLocation = {}
  error = {}

  def getAllUserAddressContext(self, data):
    addressComponents = set(())
    for address in data:
      for addressComponent in address["address_components"]:
        addressComponents.add(addressComponent['long_name'])
    
    return addressComponents

  def getOneState(self, state=None):
    for dictData in self.states:
      if dictData['name'].lower() == state.lower():
        return dictData
    return None

  def getStates(self, countryID, format=None):
    try:
      file = open('media/json/states.json', 'r', 1)
    except:
      self.error = {
        "status": True,
        "message": "State Not Found in the list."
      }
    else:
      self.states = []
      data = json.load(file)
      for dictData in data['states']:
        if dictData['country_id'] == countryID:
          self.states.append(dictData)
      self.states = sorted(self.states, key= lambda item: item['name'] )
      file.close()

  # Load current Cities
  def getCities(self, state, format=None):
    state = self.getOneState(state=state)
    if state is not None:
      try:
        file = open('media/json/cities.json', 'r', 1)
      except:
        self.error = {
          "status": True,
          "message": "State File is Missing."
        }
      else:
        self.cities = []
        data = json.load(file)
        for dictData in data['cities']:
          if dictData['state_id'].lower() == state['id'].lower():
            self.cities.append(dictData)
        self.cities = sorted(self.cities, key= lambda item: item['name'] )
        file.close()
    else:
      return "Invalid User State Location"

  def getUserInfo(self, userData):
    # gmaps = googlemaps.Client(key='AIzaSyAlu17PuCOggAb8q65PiJ2RhOkIwEzUxto')
    # gmaps = googlemaps.Client(key='AIzaSyAen5jtHmdJ5ZW3ZOCoqDVjZLkDlILJ014')
    gmaps = googlemaps.Client(key='AIzaSyDM_vyEhCa-6XerqhukIXNflsAvpqD7F8c')
    coordinates = tuple((userData['coords']['latitude'], userData['coords']['longitude']))
    reverse_geocode_result = gmaps.reverse_geocode(coordinates)
    
    addressComponents = self.getAllUserAddressContext(reverse_geocode_result)

    # Length of the address distribution
    n = len(reverse_geocode_result[0]["address_components"])

    self.userLocation = {
      "coords": {
        "latitude": userData['coords']['latitude'],
        "longitude": userData['coords']['longitude']
      },
      "addressComponents": addressComponents,
      "locality": reverse_geocode_result[0]["address_components"][n-5]["long_name"],
      "city": reverse_geocode_result[0]["address_components"][n-4]["long_name"],
      "state": reverse_geocode_result[0]["address_components"][n-3]["long_name"],
      "country": reverse_geocode_result[0]["address_components"][n-2]["long_name"],
      "pincode": reverse_geocode_result[0]["address_components"][n-1]["long_name"]
    }

  # Post Method 
  def post(self, request, format=None):
    self.error = {
      "status": False,
      "message": ""
    }
    self.getUserInfo(request.data)
    self.getStates('101')
    self.getCities(state=self.userLocation["state"])

    if self.error["status"]:
      return Response(self.error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
      "userLocation": self.userLocation,
      "stateList": self.states,
      "cityList": self.cities
    })

class ListSpecialities(APIView):
  permission_classes = (AllowAny,)

  def get(self, request, format=None):
    try:
      file = open('static/json/specialities.json', 'r', 1)
    except:
      return Response("Specialities File is Missing.")
    else:
      print(request.META)
      data = json.load(file)
      file.close()
      for dictData in data['specialities']:
        dictData['icon'] = request.META['wsgi.url_scheme']+'://'+request.META['HTTP_HOST']+dictData['icon']
      return Response(data['specialities'])