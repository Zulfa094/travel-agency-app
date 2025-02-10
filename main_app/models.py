from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main_app:destination_detail', kwargs={'pk': self.pk})


class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    destinations = models.ManyToManyField(Destination) # A package can have many destinations.

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main_app:package_detail', kwargs={'pk': self.pk})

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    booking_date = models.DateField()
    number_of_guests = models.IntegerField(default=1) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True) 

    status_choices = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')


    def __str__(self):
        return f"Booking for {self.package.name} by {self.user.username}"

    def get_absolute_url(self):
        return reverse('main_app:booking_detail', kwargs={'pk': self.pk})