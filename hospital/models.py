from django.db import models
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import date, datetime, timedelta
from annoying.functions import get_object_or_None
from django.utils.timezone import now
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Hospital(models.Model):
  user = models.OneToOneField(User, default=3, on_delete=models.CASCADE)
  image_file = models.ImageField(null=True, blank=True, help_text='Upload the Hospital Name')
  name = models.CharField(max_length=100, blank=True, null=True, help_text='Enter the Name of the Hospital')
  about = models.TextField(max_length=20480, null=True, blank=True, help_text='Enter about the hospital')
  address = models.CharField(max_length=1024, null=True, blank=True, help_text='Enter Full Adress of Hospital')
  city = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the current City')
  district = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the current District')
  state = models.CharField(max_length=100, default='Kerala')
  country = models.CharField(max_length=100, default='India')
  pincode = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the Pincode')
  phone = models.CharField(max_length=100, blank=True, null=True, help_text='Hospital Contact Number List')
  api_key = models.CharField(max_length=100, blank=True, help_text='Validation/Subscription Key for the hospital')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Date of Creation')
  updated_at = models.DateTimeField(auto_now=True, help_text='Date of Change Done')
  start_date = models.DateField(null=True, blank=True, help_text='Subscription Start Date')
  valid_date = models.DateField(null=True, blank=True, help_text='Subscription End Date')
  location = models.CharField(max_length=100, null=True, blank=True, help_text='Geo coordinates of the Hospital')
  active = models.BooleanField(default=True, help_text='Validated Hospital')
  slug = models.SlugField(unique=True)


  class Meta:
    ordering = ['state']

    def __unicode__(self):
      return self.name
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.district+' '+self.city+' '+self.state)
    super(Hospital, self).save(*args, **kwargs)

  def __str__(self):
    return str(self.name)

  def get_username(self):
    return self.user.__str__()
  
  def get_doctors(self):
    doctors = Doctor.objects.filter(hospital=self.id)
    return doctors
  
  def coords(self):
    locationList = self.location.split(',')
    return (float(locationList[0]), float(locationList[1]))
  
  def get_location(self):
    locationList = self.location.split(',')
    return {
      "lat": float(locationList[0]),
      "lng": float(locationList[1]),
    }
  
  def get_hospital(self):
    return {
      "id": self.id,
      "name": self.__str__(),
      "address": self.address,
      "image_file": self.image_file.url,
      "city": self.city,
      "district": self.district,
      "state": self.state,
      "country": self.country,
      "location": self.get_location(),
      "is_subscribed": self.is_subscribed()
    }
  
  def is_subscribed(self):
    if self.start_date:
      return True
    else:
      return False
  
class Department(models.Model):
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE)
  name = models.CharField(max_length=200, null=False, blank=False, help_text='Enter the Department Name')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Visibility Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.name+" - "+self.hospital.__str__()

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.hospital.__str__())
    super(Department, self).save(*args, **kwargs)
  
  def get_hospital(self):
    return self.hospital.get_hospital()

class Service(models.Model):
  department = models.ForeignKey(Department, default=1, on_delete=models.CASCADE, help_text='Department List')
  name= models.CharField(max_length=200, null=False, blank=False, help_text='Enter the Service Name')
  cost = models.FloatField(default=0, help_text='Enter the cost of service without implant')
  cost_implant = models.FloatField(default=0, help_text='Enter the cost of service with implant')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Visibility Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.name+"- "+self.department.__str__()
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.department+' '+self.department.hospital)
    super(Service, self).save(*args, **kwargs)
  
  def get_hospital(self):
    return self.department.hospital.get_hospital()


class Event(models.Model):
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE, help_text='Hospital Name')
  name = models.CharField(max_length=200, null=False, blank=False, help_text='Enter the title for the Event')
  about = models.TextField(max_length=20480, null=True, blank=True, help_text='Enter the details of the about')
  image_file = models.ImageField(null=True, blank=False, help_text='Select Image File for the Event')
  departments = models.ManyToManyField(Department, help_text='Include the list of the departments for the Event')
  date = models.DateField(null=False, blank=False, help_text='Event Start Date')
  event_file = models.FileField(null=True, blank=True, help_text='Event Related File')
  priority = models.PositiveIntegerField(null=True, blank=True, default="0")
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.name+"- "+self.hospital.__str__()
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.hospital.__str__())
    super(Event, self).save(*args, **kwargs)

  def get_hospital(self):
    return self.hospital.get_hospital()

class AdditionalService(models.Model):
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE, help_text='Hospital List')
  name = models.CharField(max_length=100, blank=False, null=False, help_text='Enter Additional Serviec Name')
  value = models.CharField(max_length=100, blank=False, null=False, help_text='Some Value for the Additional Service')
  icon_file = models.ImageField(null=True, blank=False, help_text='Select Additional Service Icon')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.name+"-"+self.hospital.__str__()
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.hospital.__str__())
    super(AdditionalService, self).save(*args, **kwargs)
  
  def get_hospital(self):
    return self.hospital.get_hospital()
  

class Room(models.Model):
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE)
  room_type = models.CharField(max_length=100, null=False, blank=False)
  total_bed = models.IntegerField(null=False, default=0, blank=False)
  rent_ac = models.FloatField(null=True, blank=True)
  rent_nonac = models.FloatField(null=True, blank=True, help_text='Non Ac Rent')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.room_type+"- "+self.hospital.__str__()

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.room_type+' '+self.hospital.__str__())
    super(Room, self).save(*args, **kwargs)
  
  def get_hospital(self):
    return self.hospital.get_hospital()

class HR(models.Model):
  hospital = models.ForeignKey(Hospital, default=1, on_delete=models.CASCADE)
  name = models.CharField(max_length=100, null=False, blank=False, help_text='HR Name')
  category = models.CharField(max_length=100, null= False, blank=True, default='Select Department')
  total = models.IntegerField(default=0, blank=True, null=False)
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return str(self.name+"-"+self.category+"-"+self.hospital.__str__())
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+' '+self.category+' '+self.hospital.__str__())
    super(HR, self).save(*args, **kwargs)

  def get_hospital(self):
    return self.hospital.get_hospital()

class Doctor(models.Model):
  hospital = models.ForeignKey(Hospital, default=3, on_delete=models.CASCADE, help_text='Hospital Name')
  name = models.CharField(max_length=100, null=True, blank=False, help_text='Enter the doctor name')
  department = models.ForeignKey(Department, default=1,null=True, on_delete=models.SET_NULL, help_text='Select the practive of the doctor')
  time_slot = models.CharField(max_length=100, null=True, blank=True, help_text='Visiting Time Slots')
  experience = models.IntegerField(default=1, help_text='Enter Doctor Experience')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.name+' '+self.department+' '+self.hospital.__str__())
    super(Doctor, self).save(*args, **kwargs)
  
  def get_department(self):
    return self.department.name

  def get_hospital(self):
    return self.hospital.get_hospital()

class Report(models.Model):
  user = models.ForeignKey(User, default=2, on_delete=models.SET_DEFAULT)
  content_type = models.ForeignKey(ContentType, default=12, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField(default=1)
  content_object = GenericForeignKey('content_type', 'object_id')
  message = models.CharField(max_length=20480, null=False, blank=False)
  seen = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.user.__str__()+"- "+str(self.content_type.model)+": "+self.message
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify('report '+str(self.created_at.timestamp()))
    super(Report, self).save(*args, **kwargs)

class Feedback(models.Model):
  user = models.ForeignKey(User, default=2, on_delete=models.SET_DEFAULT, help_text='Sender Details of the Feedback')
  to = models.ForeignKey(Hospital, default=3, on_delete= models.CASCADE, help_text='Hospital to which feedback has been send')
  message = models.CharField(max_length=20480, null=False, blank=False, help_text='Feedback Message to hospital')
  seen = models.BooleanField(default=False, help_text='This indicates that feedback has been seen by hospital')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return self.user.__str__()+"- "+self.to.__str__()

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify('feedback '+str(self.created_at.timestamp()))
    super(Feedback, self).save(*args, **kwargs)

class ImageGallery(models.Model):
  hospital = models.ForeignKey(Hospital, default=3, on_delete=models.SET_DEFAULT)
  image_file = models.ImageField(null=True, blank=True, help_text='select jpg or png only.')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return str(self.image_file)+"-"+str(self.hospital)

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify(self.image_file+' '+self.hospital.__str__())
    super(ImageGallery, self).save(*args, **kwargs)

class Rating(models.Model):
  user = models.ForeignKey(User, default=2, on_delete=models.SET_DEFAULT)
  content_type = models.ForeignKey(ContentType, default=12, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField(default=1)
  content_object = GenericForeignKey('content_type', 'object_id')
  rating = models.IntegerField(default=1, null=False, blank=False, validators=[MinValueValidator(1), MaxValueValidator(5)],  help_text='Select Rating out of 5')
  recommended = models.BooleanField(default=True, null=False, blank=False, help_text='Select Recommendation')
  content = models.TextField(help_text='Enter the comment')
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return str(self.content)+"-"+str(self.user)
  
  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify('comment '+self.user+' '+str(self.created_at.timestamp()))
    super(Rating, self).save(*args, **kwargs)

class Review(models.Model):
  user = models.ForeignKey(User, default=2, on_delete=models.SET_DEFAULT)
  content_type = models.ForeignKey(ContentType, default=12, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField(default=1)
  content_object = GenericForeignKey('content_type', 'object_id')
  recommended = models.BooleanField(default=True, null=False, blank=False)
  created_at = models.DateTimeField(auto_now_add=True, help_text='Created Date')
  updated_at = models.DateTimeField(auto_now=True, help_text='Updated Date')
  active = models.BooleanField(default=True, help_text='Activation Symbol')
  slug = models.SlugField(unique=True)


  def __str__(self):
    return str(self.recommended)+"-"+str(self.user)

  def save(self, *args, **kwargs):
    if not self.id:
      self.created_at = now()
    self.updated_at = now()
    self.slug = slugify('review '+self.user+' '+str(self.created_at.timestamp()))
    super(Review, self).save(*args, **kwargs)