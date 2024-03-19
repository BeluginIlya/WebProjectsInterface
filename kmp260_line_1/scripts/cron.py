import schedule
import time
from datetime import timedelta, datetime
from django.utils import timezone
from ..models import LocalPrintHistory

def monthly_cleanup():
    # Очистка записей старше 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=7)
    LocalPrintHistory.objects.filter(Timestamp__lt=thirty_days_ago).delete()
    print('clean db')


schedule.every(7).days.at("00:00").do(monthly_cleanup)
# schedule.every(10).seconds.do(monthly_cleanup)


while True:
    schedule.run_pending()
    time.sleep(1)