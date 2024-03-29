"""
URL configuration for WebInterfaceForProjects project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import index
from kmp260_line_1.views import LocalPrintHistoryAPI, PrintStatusAPI, kpm_line_1_page, end_product

app_name = "main"

urlpatterns = [
    path('', index, name="index"),
    path('kpm_line_1/', kpm_line_1_page, name="kpm_line_1"),
    path('api/local_print_history/', LocalPrintHistoryAPI.as_view(), name='local_print_history_api'),
    path('api/printer_status', PrintStatusAPI.as_view(), name='printer_status'),
    path('api/end_product', end_product,  name='end_product'),
]
