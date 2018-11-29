from django.contrib import admin
from .models import Hospital, Department, Service, AdditionalService, HR, Report, Feedback, Doctor, ImageGallery, Rating, Review, Room
from django.contrib.contenttypes.models import ContentType

# Register your models here.
admin.site.register(Hospital)
admin.site.register(Department)
admin.site.register(Service)
admin.site.register(AdditionalService)
admin.site.register(HR)
admin.site.register(Report)
admin.site.register(Feedback)
admin.site.register(Doctor)
admin.site.register(ImageGallery)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(Room)
admin.site.register(ContentType)