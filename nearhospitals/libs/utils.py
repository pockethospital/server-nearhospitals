import http.client
from rest_framework.renderers import JSONRenderer, json

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