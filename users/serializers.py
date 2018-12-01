from rest_framework import serializers
from . import models

class UsersSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Users
    fields = '__all__'
    
class FavoriteSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Favorite
    fields = '__all__'

class VisitSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Visit
    fields = '__all__'

class PaymentTransactionSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.PaymentTransaction
    fields = '__all__'
    
class AppointmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Appointment
    fields = '__all__'
class HelpSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Help
    fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = models.History
    fields = '__all__'

class SavedCardSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.SavedCard
    fields = '__all__'
    
class WalletSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Wallet
    fields = '__all__'
    
class MedicalRecordUploadSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.MedicalRecordUpload
    fields = '__all__'

class MedicalRecordSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.MedicalRecord
    fields = '__all__'

class ReminderSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Reminder
    fields = '__all__'
