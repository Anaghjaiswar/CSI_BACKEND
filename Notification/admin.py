from django.contrib import admin
from .models import Notification, DeviceToken

# Register your models here.
admin.site.register(Notification)
admin.site.register(DeviceToken)