from django.db import models

class LocalPrintHistory(models.Model):
    PalNo = models.IntegerField(null=True)
    NumProd = models.IntegerField(null=True)
    Product = models.TextField(null=True)
    Timestamp = models.CharField(max_length=255, null=True)
    Barcode = models.CharField(max_length=255, null=True)
    StatusPrint = models.BooleanField()
    add_datatime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LocalPrintHistory'

# {'item_1': {'PalNo': 33, 'NumProd': 1, 'Product': '3НСг-747.299.33-7-4', 'Timestamp': '2024-1-18   Л1 П33', 'Barcode': '131982', 'StatusPrint': False}} 