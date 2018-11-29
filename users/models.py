from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import Permission, User
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from annoying.functions import get_object_or_None
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import date, datetime, timedelta
from hospital.models import Hospital, Department


# Create your models here.
class Users(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  image_file = models.ImageField(null=True, blank=True)
  mobile = models.CharField(max_length=15, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return self.user.username

  def save(self, *args, **kwargs):
    self.slug = slugify(self.user.username)
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    super(Users, self).save(*args, **kwargs)
  
  def get_account(self):
    return {
      "id": self.user.id,
      "username": self.user.username,
      "email": self.user.email,
      "first_name": self.user.first_name,
      "last_name": self.user.last_name,
      "is_active": self.user.is_active,
      "is_superuser": self.user.is_superuser,
      "is_staff": self.user.is_staff,
      "created_at": self.created_at,
      "updated_at": self.updated_at
    }
  
class Favorite(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.SET_DEFAULT)
  hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
  favorite = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return str(self.hospital.title)+"-"+str(self.user.user.username)

class Visit(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.SET_DEFAULT)
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE)
  visibility = models.BooleanField(default=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return str(self.user)+" - "+str(self.hospital)

class PaymentTransaction(models.Model):
  transaction_id = models.TextField()
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.transaction_id)

  def save(self, *args, **kwargs):
    self.slug = slugify(self.transaction_id)
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    super(PaymentTransaction, self).save(*args, **kwargs)

class Appointment(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.SET_DEFAULT, null=True)
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.SET_NULL, null=True)
  department = models.ForeignKey(Department, default=1, on_delete=models.SET_NULL, null=True)
  phone = models.TextField(max_length=20, blank=True, null=True)
  aadharNumber = models.TextField(max_length=12, blank=True, null=True)
  date = models.DateField(blank=False, null=False)
  time = models.TimeField(blank=False, null=False)
  payment_status = models.TextField()
  visibility = models.BooleanField(default=True)
  transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.user)+" - "+str(self.hospital)

  def save(self, *args, **kwargs):
    self.slug = slugify(self.aadharNumber+' '+str(self.created_at.timestamp()))
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    super(Appointment, self).save(*args, **kwargs)

class Help(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.SET_NULL, null=True)
  query = models.TextField(max_length= 10240 , blank=False, null=False)
  content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
  object_id = models.PositiveIntegerField(default=1)
  content_object = GenericForeignKey('content_type', 'object_id')
  status = models.CharField(max_length=50, blank=False, null=False, default='OPEN')
  visibility = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.slug)+" - "+str(self.user)+" - "+str(self.created_at)+"-"+str(self.updated_at)
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    print(self.created_at)
    print(self.updated_at)
    self.slug = slugify('help '+ str(self.created_at.timestamp()))
    super(Help, self).save(*args, **kwargs)

class History(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.SET_NULL, null=True)
  searched = models.TextField(max_length=1024, blank=False, null=False)
  visibility = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return str(self.user)+" - "+str(self.searched)

class SavedCard(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.CASCADE, null=True)
  nameOnCard = models.CharField(max_length=100, blank=True, null=False, default='')
  cardNumber = models.CharField(max_length=50, blank=True, null=False, default='')
  validMonth = models.CharField(max_length=2, blank=True, default='')
  validYear = models.CharField(max_length=2, blank=True, default='')
  savedAs = models.CharField(max_length=150, blank=True, null=False, default='')
  bankName = models.CharField(max_length=200, blank=True, null=False, default='')
  cardType = models.CharField(max_length=50, blank=True, null=False, default='')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.savedAs+"-"+self.bankName

class Wallet(models.Model):
  user = models.OneToOneField(Users, default=1, on_delete=models.CASCADE, null=True)
  amount = models.FloatField(default=0.0, null=False, blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.amount)

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify('wallet '+ str(self.user.user.username))
    super(Wallet, self).save(*args, **kwargs)

class MedicalRecordUpload(models.Model):
  uploadFile = models.FileField(upload_to='uploads/users/%Y/%m/%d/')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.uploadFile)+'-'+str(self.created_at.timestamp())

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(str(self.uploadFile)+' '+str(self.created_at.timestamp()))
    super(MedicalRecordUpload, self).save(*args, **kwargs)


class MedicalRecord(models.Model):
  user = models.ForeignKey(Users, default=1, on_delete=models.CASCADE, null=True)
  recordName = models.CharField(max_length=1024, blank=False, null=False, default='New Record')
  uploadedDocs = models.ManyToManyField(MedicalRecordUpload)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.user)+'-'+str(self.recordName)

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(str(self.user.user.username) +' '+ str(self.recordName) )

    # exists = MedicalRecord.objects.filter(slug=self.slug).exists()
    # if exists:
    #   self.slug = "%s-%s" %(self.slug, self.id)
    super(MedicalRecord, self).save(*args, **kwargs)

class Reminder(models.Model):
  DAILY = 'DA'
  SELECTED_DAYS_OF_WEEK = 'SD'
  INTERVAL_OF_DAYS = 'ID'

  REPEAT_CHOICES = (
    (DAILY, 'Daily'),
    (SELECTED_DAYS_OF_WEEK, 'Selected Day(s) Of Week'),
    (INTERVAL_OF_DAYS, 'In Interval of Days')
  )

  user = models.ForeignKey(Users, default=1, on_delete=models.CASCADE, null=True)
  name = models.CharField(max_length=1024, blank=False, null=False, default='New Reminder')
  frequency = models.PositiveIntegerField(default=1, null=False, blank=False)
  alarms = models.CharField(max_length=1024, blank=False, null=False)
  repeat = models.CharField(max_length=2, choices=REPEAT_CHOICES, default=DAILY, blank=False, null=False)
  startDate = models.DateField(default=now, blank=False, null=False)
  intervalGap = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(2), MaxValueValidator(100)])
  daysOfWeek = models.CharField(max_length=1024, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.user)+'-'+str(self.name)

  def getFrequencyAndAlarms(self):
    return

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(str(self.user.user.username) +' '+ str(self.name) +' '+ str(self.created_at.timestamp()))
    super(Reminder, self).save(*args, **kwargs)