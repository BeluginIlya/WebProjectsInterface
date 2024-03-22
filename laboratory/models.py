from django.db import models


class BaseForWrite(models.Model):
    server = models.CharField(max_length=100)
    base = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    nameBaseTable = models.CharField(max_length=100)
    

class Line(models.Model):
    LineName = models.CharField(max_length=60)
    TimeSecUpdate = models.IntegerField()
    base = models.ForeignKey(BaseForWrite, on_delete=models.DO_NOTHING)

class PLC(models.Model):
    PLCName = models.CharField(max_length=100)
    chamber = models.CharField(max_length=100)
    adress = models.CharField(max_length=100)
    line_id = models.ForeignKey(Line, on_delete=models.CASCADE)

class CurtecSensors(models.Model):
    TimeStamp = models.DateTimeField(auto_now_add=True)
    ValueName = models.CharField(max_length=255)
    Value = models.FloatField()
    PLC = models.ForeignKey(PLC, on_delete=models.CASCADE)