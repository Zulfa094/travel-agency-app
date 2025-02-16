from django.contrib import admin
from .models import Destination, Package, Booking, Notification

# Register models
admin.site.register(Destination)
admin.site.register(Package)
admin.site.register(Booking)
admin.site.register(Notification)