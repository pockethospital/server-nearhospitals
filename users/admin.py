from django.contrib import admin
from .models import Users, PaymentTransaction, Favorite, Visit, Appointment, Help, History, Wallet, SavedCard, MedicalRecord, MedicalRecordUpload, Reminder
# Register your models here.

admin.site.register(Users)
admin.site.register(PaymentTransaction)
admin.site.register(Favorite)
admin.site.register(Visit)
admin.site.register(Appointment)
admin.site.register(Help)
admin.site.register(History)
admin.site.register(Wallet)
admin.site.register(SavedCard)
admin.site.register(MedicalRecord)
admin.site.register(MedicalRecordUpload)
admin.site.register(Reminder)