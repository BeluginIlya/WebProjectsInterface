# serializers.py
from rest_framework import serializers
from .models import LocalPrintHistory

class LocalPrintHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalPrintHistory
        fields = '__all__'
