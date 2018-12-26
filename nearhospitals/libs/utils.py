import http.client
from rest_framework.renderers import JSONRenderer, json
import os
from sendgrid.helpers.mail import *
import sendgrid

def getHostName():
  return 'http://localhost:8000'

# SMS Sending API Methods
class SMSVerificationSystem:

  conn = http.client.HTTPConnection("2factor.in")
  headers = { 'content-type': "application/x-www-form-urlencoded" }
  SMS_API = "c1ca6fa8-f629-11e8-a895-0200cd936042"
  
  
  templates = {
    "USER_REGISTRATION": "user-registration",
    "USER_PASSWORD_RECOVERY": "password-recovery"
  }

  def leftTotalOTPSMS(self):
    payload = ""
    url = "/API/V1/"+self.SMS_API+"/BAL/SMS"
    print(url)
    self.conn.request("GET", url, payload, self.headers)
    res = self.conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))
    if result['Status'] == 'Success':
      return result['Details']
    else:
      return None

  def checkLeftPromotionalSMS(self):
    payload = ""
    url = "/"+self.SMS_API+"/ADDON_SERVICES/BAL/PROMOTIONAL_SMS"
    print(url)
    self.conn.request("GET", url, payload, self.headers)
    res = self.conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))
    if result['Status'] == 'Success':
      return result['Details']
    else:
      return None

  def userOTPVerification(self, phoneNumber, template):
    payload = ""
    totalSMS = self.leftTotalOTPSMS()
    if len(phoneNumber) != 10:
      return {
        "Status": "Error",
        "Details": "Mobile Number is Incorrect"
      }
    print(totalSMS)
    if totalSMS is None or int(totalSMS) <= 10:
      return {
        "Status": "Error",
        "Details": "SMS API Related Issue"
      }

    self.conn.request("GET", "/API/V1/"+self.SMS_API+"/SMS/"+phoneNumber+"/AUTOGEN/"+self.templates[template], payload, self.headers)
    res = self.conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))

    return result

  def userOTPValidation(self, otp=None, session=None):
    payload = ""
    if otp is None or len(otp) != 6:
      return {
        "Status": "Error",
        "Details": "Invalid OTP"
      }
    
    if session is None:
      return {
        "Status": "Error",
        "Details": "Invalid Session"
      }

    url = "/API/V1/"+self.SMS_API+"/SMS/VERIFY/"+session+"/"+otp
    self.conn.request("GET", url, payload, self.headers)

    res = self.conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))

    return result

  def sendPromotionalSMS(self, phoneNumber):
    payload = ""
    totalSMS = self.checkLeftPromotionalSMS()
    if len(phoneNumber) != 10:
      return {
        "Status": "Error",
        "Details": "Mobile Number is Incorrect"
      }
    if totalSMS is None or int(totalSMS) <= 10:
      return {
        "Status": "Error",
        "Details": "SMS API Related Issue"
      }

    url = "/"+self.SMS_API+"/ADDON_SERVICES/SEND/PSMS"
    self.conn.request("GET", url, payload, self.headers)


    res = self.conn.getresponse()
    data = res.read()
    result = json.loads(data.decode("utf-8"))

    return result

# Returns clients IP address from the request parameter
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class SendEmail:

  sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
  
  def sendEmail(self):
    from_email = Email("winmacinux@gmail.com")
    to_email = Email("technical.pockethospital@gmail.com")
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")

    mail = Mail(from_email, subject, to_email, content)
    response = self.sg.client.mail.send.post(request_body=mail.get())

    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response

class LocationFile:
  stateFile = None
  cityFile = None
  allCityFile = None
  states = []
  cities = []
  error = {}

  def __init__(self):
    stateFileName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/states.json' 
    cityFileName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/top-cities.json'
    allCityFileName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/static/json/new-cities.json'

    try:
      self.stateFile = open(stateFileName, 'r', 1) 
    except:
      self.error = {
        "status": True,
        "message": "State Not Found in the list."
      }
    else:
      self.states = []
    
    try:
      self.cityFile = open(cityFileName, 'r', 1)
    except:
      self.error = {
        "status": True,
        "message": "City Not Found in the list."
      }
    else:
      self.cities = []
    
    try:
      self.allCityFile = open(allCityFileName, 'r', 1)
    except:
      self.error = {
        "status": True,
        "message": "All City Not Found in the list."
      }
    else:
      self.cities = []

  # Destructor Defination
  def __del__(self):
    print("Delete")
    self.stateFile.close()
    self.cityFile.close()
    self.allCityFile.close()

  # States Methods Definations
  def getAllStates(self):
    if self.error:
      return self.error
    
    self.states = []
    data = {}
    data = json.load(self.stateFile)
    for dictData in data['states']:
      dictData['icon'] = getHostName()+dictData['icon']
      self.states.append(dictData)
    self.states = sorted(self.states, key= lambda item: item['name'] )
    return self.states
  
  def makeQuickState(self, nearStates):
    if self.error:
      return self.error
    
    self.states = []
    data = json.load(self.stateFile)
    for dictData in data['states']:
      for nearState in nearStates:
        if nearState.lower() == dictData['name'].lower():
          dictData['quick'] = True
      dictData['icon'] = getHostName()+dictData['icon']
      self.states.append(dictData)
    self.states = sorted(self.states, key= lambda item: item['name'] )
    return self.states

  def getStateDetails(self, stateId=None, stateName=None):
    if self.error:
      return self.error
    if stateId is not None:
      return filter(lambda item: (item['id'] == stateId), self.getAllStates())
    elif stateName is not None:
      return filter(lambda item: (item['name'].lower() == stateName.lower()), self.getAllStates())
    else:
      return []


  
  def isState(self, stateName):
    if self.error:
      return self.error
    if len(list(filter(lambda item: (item['name'].lower() == stateName.lower()), self.getAllStates()))) > 0:
      return True
    else:
      return False

  # Cities Methods Defination
  def getAllCities(self):
    if self.error:
      return self.error
    
    self.cities = []
    data = json.load(self.cityFile)
    for dictData in data['cities']:
      # title=dictData["name"]
      # title = title.strip(" ,")
      # maketrans = title.maketrans
      # dictData["icon"] = "/assets/icons/cities/"+title.translate(maketrans(' ', '_')).lower()+"_icon.jpg"
      self.cities.append(dictData)
    self.cities = sorted(self.cities, key= lambda item: item['name'] )
    return self.cities
  
  def getTopCities(self):
    if self.error:
      return self.error
    
    self.cities = []
    data = json.load(self.cityFile)
    self.cities = filter(lambda item: (item['quick'] == True), data["cities"])
    self.cities = sorted(self.cities, key= lambda item: item['name'] )
    return self.cities
  
  def getStateCities(self, stateID):
    if self.error:
      return self.error
    
    self.cities = []
    data = json.load(self.allCityFile)

    self.cities = filter(lambda item: (item['state_id'] == stateID), data["cities"])
    self.cities = sorted(self.cities, key= lambda item: item['name'] )
    for data in self.cities:
      data['icon'] = getHostName()+data['icon']

    # print(self.cities)
    return self.cities

  # def getStateDetails(self, cityName):
  #   if self.error:
  #     return self.error
  #   return list(filter(lambda item: (item['name'].lower() == cityName.lower()), ))[0]
  
  # def isState(self, stateName):
  #   if self.error:
  #     return self.error
  #   if len(list(filter(lambda item: (item['name'].lower() == stateName.lower()), self.getAllStates()))) > 0:
  #     return True
  #   else:
  #     return False
