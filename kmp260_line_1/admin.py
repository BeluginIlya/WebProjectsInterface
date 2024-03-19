from django.contrib import admin
from .models import LocalPrintHistory

@admin.register(LocalPrintHistory)
class LocalPrintHistoryAdmin(admin.ModelAdmin):
    list_display = ('PalNo', 'NumProd', 'Timestamp', 'Barcode', 'Product', 'StatusPrint')
    search_fields = ('PalNo', 'Barcode', 'Product')
    list_filter = ('StatusPrint',)
    ordering = ('-Timestamp',)
