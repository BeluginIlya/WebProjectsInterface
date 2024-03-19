# В файле laboratory/forms.py

from django import forms
from .models import Line, BaseForWrite, PLC, CurtecSensors

class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        fields = ['LineName']

class BaseForWriteForm(forms.ModelForm):
    class Meta:
        model = BaseForWrite
        fields = ['server', 'base', 'table', 'user', 'password', 'line']

class PLCForm(forms.ModelForm):
    class Meta:
        model = PLC
        fields = ['PLCName', 'adress', 'line']

class CurtecSensorsForm(forms.ModelForm):
    class Meta:
        model = CurtecSensors
        fields = ['ValueName', 'Value', 'PLC']
