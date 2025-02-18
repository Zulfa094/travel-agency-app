from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError

class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('destination_detail', kwargs={'pk': self.pk})

class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    destinations = models.ManyToManyField(Destination)
    available_dates = models.TextField(default='[]')  # Store as JSON string
    spots_per_date = models.PositiveIntegerField(default=10)

    def get_available_dates(self):
        import json
        return json.loads(self.available_dates)

    def set_available_dates(self, dates):
        import json
        self.available_dates = json.dumps(dates)

    def add_available_dates(self, start_date, end_date):
        """Add a range of available dates to the package"""
        current = start_date
        dates = []
        while current <= end_date:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timezone.timedelta(days=1)
        self.set_available_dates(dates)
        self.save()

    def get_spots_available(self, date):
        """Get number of spots available for a specific date"""
        from django.db.models import Sum
        
        if str(date) not in self.get_available_dates():
            return 0
            
        booked_spots = self.bookings.filter(
            booking_date=date,
            status__in=['pending', 'approved']
        ).aggregate(
            total=Sum('number_of_guests')
        )['total'] or 0
        
        return max(0, self.spots_per_date - booked_spots)

    def is_fully_booked(self, date):
        """Check if a specific date is fully booked"""
        return self.get_spots_available(date) == 0

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('package_detail', kwargs={'pk': self.pk})

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.booking_date:
            # Check if date is available
            if str(self.booking_date) not in self.package.get_available_dates():
                raise ValidationError('This date is not available for booking')
            
            # Check if there are enough spots available
            current_bookings = Booking.objects.filter(
                package=self.package,
                booking_date=self.booking_date
            ).exclude(pk=self.pk).aggregate(
                total_guests=models.Sum('number_of_guests')
            )['total_guests'] or 0
            
            if current_bookings + self.number_of_guests > self.package.spots_per_date:
                raise ValidationError('Not enough spots available for this date')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s booking for {self.package.name} on {self.booking_date}"

    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Create notification for superusers when a new booking is made
            Notification.objects.create(
                booking=self,
                message=f"New booking request from {self.user.username} for {self.package.name}",
                notification_type='new_booking'
            )

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_booking', 'New Booking'),
        ('booking_approved', 'Booking Approved'),
        ('booking_rejected', 'Booking Rejected'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_for_superuser = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.created_at}"