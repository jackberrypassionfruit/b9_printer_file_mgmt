from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("printer-display/", views.printer_display, name="printer_display"),
    path("get-printers/", views.get_printers, name="get_printers"),
]
