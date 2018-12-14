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
import os
from nearhospitals.libs.utils import SMSVerificationSystem 

# Create your views here.

# If you want to make the data request from the same domain of the server. 

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
  username = request.data.get("username")
  password = request.data.get("password")

  usernameRegex = r'^[A-Za-z]+[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$'
  phoneRegex = r'^[0-9]{5,}$'
  

  if re.match(phoneRegex, request.data.get("username"), flags=0) is not None:
    userObj = get_object_or_None(models.Users, mobile=username)
    # print(userObj.user.username)
    if userObj is None:
      return Response({ 
        "statusMessage": "Invalid Mobile Number",
        "isMobile": True,
        "isUsername": False
        }, status= status.HTTP_401_UNAUTHORIZED ) 
    user = authenticate(username=userObj.user.username, password=password)
    if not user:
      users = get_object_or_None(models.Users, mobile=username)
      if users is not None:
        return Response({ 
          "statusMessage": "Password is not correct.",
          "isMobile": True,
          "isUsername": False
          }, status= status.HTTP_401_UNAUTHORIZED )
  
  
  elif re.match(usernameRegex, request.data.get("username"), flags=0) is not None:
    user = authenticate(username=username, password=password)
    if not user:
      users = get_object_or_None(models.Users, user__username=username)
      if users is not None:
        return Response({ 
          "statusMessage": "Password is not correct.",
          "isMobile": False,
          "isUsername": True
          }, status= status.HTTP_401_UNAUTHORIZED )
      else:
        return Response({ 
          "statusMessage": "Invalid Username",
          "isMobile": False,
          "isUsername": True
          }, status= status.HTTP_401_UNAUTHORIZED )

  token, _ = Token.objects.get_or_create(user=user)
  return Response(
    {
      "statusMessage": "Successfully Logged In",
      "shortName": user.get_short_name() if len(user.get_short_name()) > 0 else username,
      "token": token.key
    }, status=status.HTTP_200_OK)
    

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def checkUserExistence(request):
  cred = request.data.get("cred")

  usernameRegex = r'^[A-Za-z]+[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$'
  phoneRegex = r'^[0-9]{5,}$'

  isMobile = False 
  isUsername = False

  if checkExistence(cred):
    if re.match(phoneRegex, cred, flags=0) is not None:
      isMobile = True
    elif re.match(usernameRegex, cred, flags=0) is not None:
      isUsername = True
      
    if get_object_or_None(models.Users, user__username= cred) is not None or get_object_or_None(models.Users, mobile= cred) is not None:
      return Response({ 
        "statusMessage": "User Exist",
        "isMobile": isMobile,
        "isUsername": isUsername,
        }, status=status.HTTP_200_OK )
    else:
      return Response({ 
        "statusMessage": "User Doesn't Exist",
        "isMobile": isMobile,
        "isUsername": isUsername,
        }, status=status.HTTP_401_UNAUTHORIZED )
  else:
    return Response({ 
      "statusMessage": "Parameter's Missing"
      }, status=status.HTTP_400_BAD_REQUEST )





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
  
  if get_object_or_None(models.Users, mobile= username) is not None:
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
        "shortName": user.get_short_name() if len(user.get_short_name()) > 0 else username,
        "token": token.key
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
          "statusMessage": "Password has been changed successfully"
        })
      else:
        return Response({ "statusMessage": "New Password is missing" }, status= status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({ "statusMessage": "Password is already changed. Invalid Link" }, status= status.HTTP_401_UNAUTHORIZED)
  else:
    return Response({ "statusMessage": "Invalid username" }, status= status.HTTP_401_UNAUTHORIZED)

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
      return Response({"statusMessage": "Invalid Email ID"}, status= status.HTTP_401_UNAUTHORIZED)
  elif re.match(usernameRegex, request.data.get("cred"), flags=0) is not None:
    user = get_object_or_None(User, username=request.data.get("cred"))
    if user is None:
      return Response({ "statusMessage": "Invalid Username"}, status= status.HTTP_401_UNAUTHORIZED )
  elif re.match(phoneRegex, request.data.get("cred"), flags=0) is not None:
    users = get_object_or_None(models.Users, mobile=request.data.get("cred"))
    if users is not None:
      user = users.user
    else:
      return Response({ "statusMessage": "Invalid Phone Number" }, status= status.HTTP_401_UNAUTHORIZED )
  else:
    return Response({ "statusMessage": "Invalid Credential. Check Your Input" }, status= status.HTTP_401_UNAUTHORIZED)

  subject = "Pocket Hospital's User Password Recovery Mail."
  message = "<a href='http://localhost:8080/forget_password/"+ user.username +"/"+ user.password +"/'>Click Here to Change Password</a>"
  sender = "Pocket Hospital"

  to = user.email
  if len(to):
    if send_mail(subject, message, sender, [to], fail_silently=False):
      return Response({
        "statusMessage": "Mail sent to the registered email Id"
      })
    else:
      return Response({ "statusMessage": "Techincal Issue Can't send mail. Contact at technical@pockethospital.com" }, status= status.HTTP_401_UNAUTHORIZED)
  else:
      return Response({ "statusMessage": "No Email Id is Registered with us. Contact at technical@pockethospital.com" }, status= status.HTTP_401_UNAUTHORIZED)


# Change the User AUthenticatin Password With Old Password 
@api_view(["PUT"])
@csrf_exempt
def ChangeUserPassword(request):

  if checkExistence(request.data.get("slug")) and checkExistence(request.data.get("newPassword")) and checkExistence(request.data.get("oldPassword")):  

    user = get_object_or_None(models.Users, slug=request.data.get("slug"))
    if not user:
        return Response({ "statusMessage": "Invalid Username"}, status= status.HTTP_401_UNAUTHORIZED )
    else:
      if check_password(password=request.data.get("oldPassword"), encoded=user.user.password):
        if len(request.data.get("newPassword")) < 6:
          return Response({ "statusMessage": "New password length minimum 6"}, status= status.HTTP_401_UNAUTHORIZED ) 
        newPassword = make_password(password=request.data.get("newPassword")) 
        user.user.password = newPassword
        user.save()
        return Response({
          "statusMessage": "Password Has Been Changed Successfully"
        })
      else:
        return Response({ "statusMessage": "Invalid Old Password"}, status= status.HTTP_401_UNAUTHORIZED )
  else:
    return Response({ "statusMessage": "Inputs are missing"}, status= status.HTTP_401_UNAUTHORIZED )



# User Profile Classes
class UserProfile(generics.RetrieveAPIView):
  serializer_class = serializers.UsersSerializer
  queryset = models.Users.objects.all()
  permission_classes = ""


class GetState(APIView):
  permission_classes = (AllowAny,)

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
      file = open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/states.json', 'r', 1)
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
        file = open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/cities.json', 'r', 1)
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

  # Get Method 
  def get(self, request, format=None):
    self.error = {
      "status": False,
      "message": ""
    }
    self.getStates('101')

    if self.error["status"]:
      return Response(self.error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
      "stateList": self.states,
    })

class ListSpecialities(APIView):
  permission_classes = (AllowAny,)

  def get(self, request, format=None):
    try:
      file = open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/specialities.json', 'r', 1)
    except:
      return Response("Specialities File is Missing.")
    else:
      # print(request.META)
      data = json.load(file)
      file.close()
      for dictData in data['specialities']:
        dictData['icon'] = request.META['wsgi.url_scheme']+'://'+request.META['HTTP_HOST']+dictData['icon']
      return Response(data['specialities'])

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def userOTPVerification(request):
  smsService = SMSVerificationSystem()

  phoneRegex = r'^[0-9]{10}$'
  template = request.data.get("templateName")
  phoneNumber = request.data.get("phoneNumber")

  print(re.match(phoneRegex, phoneNumber, flags=0))
  if phoneNumber is None or template is None:
    return Response("Invalid Parameters", status=status.HTTP_400_BAD_REQUEST)

  if re.match(phoneRegex, phoneNumber, flags=0) is None:
    return Response("Invalid Phone Number", status=status.HTTP_400_BAD_REQUEST)

  result = smsService.userOTPVerification(phoneNumber, template)
  return Response(result)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def userOTPValidation(request):
  smsService = SMSVerificationSystem()

  otp = request.data.get("otp")
  session = request.data.get("session")

  if otp is None or otp is None:
    return Response("Invalid Parameters", status=status.HTTP_400_BAD_REQUEST)

  result = smsService.userOTPValidation(otp, session)
  
  if result['Status'] == 'Error':
    return Response(result, status=status.HTTP_400_BAD_REQUEST)

  if result['Status'] == 'Success' and result['Details'] == 'OTP Expired':
    return Response(result, status=status.HTTP_400_BAD_REQUEST)
  
  return Response(result)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def userApplicationLink(request):
  return Response("Link sent successfully!")