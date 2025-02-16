from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Destination, Package, Booking, Notification, User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

def context_processor(request):
    context = {}
    if request.user.is_authenticated and request.user.is_superuser:
        context['pending_count'] = Booking.objects.filter(status='pending').count()
    return context

class Home(ListView):
    model = Package
    template_name = 'home.html'
    context_object_name = 'packages'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.all()
        context['destinations'] = Destination.objects.all()
        return context
    
        
       
        # if self.request.user.is_authenticated and self.request.user.is_superuser:
        #     context['pending_bookings'] = Booking.objects.filter(status='pending')
        #     context['notifications'] = Notification.objects.filter(
        #         recipient=self.request.user,
        #         is_for_superuser=True,
        #         is_read=False
        #     ).order_by('-created_at')
        
        # return context

def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

class DestinationCreate(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = Destination
    fields = ['name', 'description']
    
    def get_success_url(self):
        return reverse('destination_detail', kwargs={'pk': self.object.pk})

class DestinationUpdate(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = Destination
    fields = ['name', 'description']
    
    def get_success_url(self):
        return reverse('destination_detail', kwargs={'pk': self.object.pk})

class DestinationDelete(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = Destination
    
    def get_success_url(self):
        return reverse('destination_list')
    
class DestinationDetail(LoginRequiredMixin, DetailView):
    model = Destination
    template_name = 'main_app/destination_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.filter(destinations=self.object)
        return context

class PackageCreate(SuperUserRequiredMixin, CreateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    
    def get_success_url(self):
        return reverse('home')

class PackageUpdate(SuperUserRequiredMixin, UpdateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    
    def get_success_url(self):
        return reverse('package_detail', kwargs={'pk': self.object.pk})

class PackageDelete(SuperUserRequiredMixin, DeleteView):
    model = Package
    
    def get_success_url(self):
        return reverse('home')
    

class PackageDetail(DetailView):
    model = Package
    template_name = 'main_app/package_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = self.object.destinations.all()
        return context
    

class PackageUpdate(LoginRequiredMixin, UpdateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    def get_success_url(self):
        return redirect('package_detail', pk=self.object.pk)

class PackageDelete(LoginRequiredMixin, DeleteView):
   model = Package
   def get_success_url(self):
       return redirect('home')
   template_name = 'package_confirm_delete.html'

class PackageList(ListView):
    model = Package
    template_name = 'main_app/package_list.html'
    context_object_name = 'packages'

class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['booking_date', 'number_of_guests', 'contact_email', 'contact_phone']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        package_id = self.kwargs.get('package_id')
        context['package'] = Package.objects.get(pk=package_id)
        return context
    
    def form_valid(self, form):
        try:
            # Set the user and package
            form.instance.user = self.request.user
            package_id = self.kwargs.get('package_id')
            form.instance.package = Package.objects.get(pk=package_id)
            
            # Call parent's form_valid to save the booking
            response = super().form_valid(form)
            
            # Now create notifications for superusers
            superusers = User.objects.filter(is_superuser=True)
            for superuser in superusers:
                Notification.objects.create(
                    booking=self.object,
                    message=f"New booking request from {self.request.user.username} for {self.object.package.name}",
                    notification_type='new_booking',
                    recipient=superuser,
                    is_for_superuser=True
                )
            
            return response
        except Exception as e:
            print(f"Error in form_valid: {str(e)}")
            raise

    def get_success_url(self):
        return reverse('booking_detail', kwargs={'pk': self.object.pk})

class BookingDetail(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'main_app/booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage'] = self.request.user.is_superuser
        return context

class BookingDelete(LoginRequiredMixin, DeleteView):
    model = Booking
    def get_success_url(self):
       return redirect('home')
    template_name = 'booking_confirm_delete.html'

class ManageBookings(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'main_app/manage_bookings.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_bookings'] = Booking.objects.filter(status='pending')
        context['notifications'] = Notification.objects.filter(
            recipient=self.request.user,
            is_for_superuser=True,
            is_read=False
        ).order_by('-created_at')
        return context

@login_required
@user_passes_test(is_superuser)
@require_POST
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = Booking.STATUS_APPROVED
    booking.save()
    
    # Create notification for the booking user
    Notification.objects.create(
        booking=booking,
        message=f"Your booking has been approved",
        notification_type='booking_approved',
        recipient=booking.user,  
        is_for_superuser=False
    )
    
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_superuser)
@require_POST
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = Booking.STATUS_REJECTED
    booking.save()
    
    # Create notification for the booking user
    Notification.objects.create(
        booking=booking,
        message=f"Your booking has been rejected",
        notification_type='booking_rejected',
        recipient=booking.user,  
        is_for_superuser=False
    )
    
    return JsonResponse({'status': 'success'})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id,
        recipient=request.user  
    )
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})