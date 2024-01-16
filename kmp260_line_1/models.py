from django.db import models

class LocalPrintHistory(models.Model):
    PalNo = models.IntegerField(null=True)
    NumProd = models.IntegerField(null=True)
    Timestamp = models.DateTimeField(null=True)
    Barcode = models.CharField(max_length=255, null=True)
    Product = models.TextField(null=True)
    StatusPrint = models.BooleanField()

    class Meta:
        db_table = 'LocalPrintHistory'
