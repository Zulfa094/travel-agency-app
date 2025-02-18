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
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime
from django.urls import reverse_lazy
from django.http import JsonResponse

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
        
        # Get upcoming bookings for calendar
        if self.request.user.is_authenticated:
            context['upcoming_bookings'] = Booking.objects.filter(
                user=self.request.user,
                booking_date__gte=timezone.now().date(),
                status='approved'
            ).select_related('package')
        
        # Initialize available dates for packages that don't have any
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=30)
        
        for package in context['packages']:
            if not package.available_dates:
                package.add_available_dates(today, end_date)
        
        # Add notifications for authenticated users
        if self.request.user.is_authenticated:
            context['notifications'] = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).order_by('-created_at')
        
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

class DestinationCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Destination
    fields = ['name', 'description', 'image']
    
    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse('destination_detail', kwargs={'pk': self.object.pk})

class DestinationUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Destination
    fields = ['name', 'description', 'image']
    
    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse('destination_detail', kwargs={'pk': self.object.pk})

class DestinationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Destination
    success_url = reverse_lazy('destination_list')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        destination = self.get_object()
        destination.package_set.clear()
        response = super().delete(request, *args, **kwargs)
        return JsonResponse({'status': 'success'}) if request.is_ajax() else response
    
class DestinationDetail(LoginRequiredMixin, DetailView):
    model = Destination
    template_name = 'main_app/destination_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.filter(destinations=self.object)
        return context

class DestinationList(ListView):
    model = Destination
    template_name = 'main_app/destination_list.html'
    context_object_name = 'destinations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        return context

class PackageForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Start date for package availability'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='End date for package availability'
    )

    class Meta:
        model = Package
        fields = ['name', 'description', 'price', 'total_spots', 'destinations']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'destinations': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('End date must be after start date')
            if start_date < timezone.now().date():
                raise ValidationError('Start date cannot be in the past')

        return cleaned_data

class PackageCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Package
    form_class = PackageForm
    template_name = 'main_app/package_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add available dates after package is created
        self.object.add_available_dates(
            form.cleaned_data['start_date'],
            form.cleaned_data['end_date']
        )
        return response

class PackageUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Package
    form_class = PackageForm
    template_name = 'main_app/package_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_initial(self):
        initial = super().get_initial()
        # Get the first and last date from available_dates
        dates = self.object.get_available_dates()
        if dates:
            initial['start_date'] = datetime.strptime(dates[0], '%Y-%m-%d').date()
            initial['end_date'] = datetime.strptime(dates[-1], '%Y-%m-%d').date()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.add_available_dates(
            form.cleaned_data['start_date'],
            form.cleaned_data['end_date']
        )
        return response

class PackageDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Package
    success_url = reverse_lazy('package_list')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        package = self.get_object()
        package.booking_set.all().delete()
        response = super().delete(request, *args, **kwargs)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'redirect_url': self.success_url})
        return response

class PackageDetail(DetailView):
    model = Package
    template_name = 'main_app/package_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        package = self.object
        
        # Convert dates to proper format and add availability info
        dates = package.get_available_dates()
        if dates:
            # Sort dates chronologically
            sorted_dates = sorted(dates)
            start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').date()
            end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').date()
            context['date_range'] = {
                'start': start_date,
                'end': end_date
            }

        # Check if user has already booked this package
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            user_booking = Booking.objects.filter(
                user=self.request.user,
                package=package
            ).first()
            if user_booking:
                context['user_booking'] = user_booking
                
        return context
    

class PackageList(ListView):
    model = Package
    template_name = 'main_app/package_list.html'
    context_object_name = 'packages'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        return context

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'number_of_guests', 'contact_email', 'contact_phone', 'package']
        widgets = {
            'booking_date': forms.Select(),
            'number_of_guests': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'package': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        package = kwargs.pop('package', None)
        super().__init__(*args, **kwargs)
        
        if package:
            self.fields['package'].initial = package.id
            self.fields['package'].widget = forms.HiddenInput()
            
            # Get all bookings for each date
            bookings_by_date = (
                Booking.objects.filter(package=package)
                .values('booking_date')
                .annotate(total_guests=Sum('number_of_guests'))
            )
            
           
            booked_guests = {
                str(booking['booking_date']): booking['total_guests']
                for booking in bookings_by_date
            }
            
            # Filter available dates and create choices
            today = timezone.now().date()
            available_dates = []
            for date_str in package.get_available_dates():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if date_obj >= today:
                    booked = booked_guests.get(date_str, 0)
                    spots_left = package.total_spots - booked
                    if spots_left > 0:
                        available_dates.append(
                            (date_str, f"{date_obj.strftime('%B %d, %Y')} ({spots_left} spots left)")
                        )
            
            self.fields['booking_date'] = forms.ChoiceField(
                choices=available_dates,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'main_app/booking_form.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.package = get_object_or_404(Package, pk=kwargs.get('package_id'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['package'] = self.package
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            data['package'] = self.package.id
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.package = self.package
        form.instance.status = 'pending'
        response = super().form_valid(form)

        # Create notification for superusers
        superusers = User.objects.filter(is_superuser=True)
        for superuser in superusers:
            Notification.objects.create(
                recipient=superuser,
                message=f'New booking request from {self.request.user.username} for {self.package.name}',
                booking=form.instance,
                is_for_superuser=True
            )

        messages.success(self.request, 'Booking created successfully! Waiting for approval.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['package'] = self.package
        return context

    def get_success_url(self):
        return reverse('booking_detail', kwargs={'pk': self.object.pk})

class BookingDetail(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'main_app/booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage'] = self.request.user.is_superuser
        context['notifications'] = Notification.objects.filter(
            booking=self.object,
            recipient=self.request.user,
            is_for_superuser=False
        ).order_by('-created_at')
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

class BookingDelete(LoginRequiredMixin, DeleteView):
    model = Booking
    def get_success_url(self):
       return redirect('home')
    template_name = 'booking_confirm_delete.html'

class BookingList(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'main_app/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Regular users see their own bookings, superusers see all bookings
        if self.request.user.is_superuser:
            return Booking.objects.all().order_by('-booking_date')
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')

class BookingStatusList(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = Booking
    template_name = 'main_app/booking_status_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        status = self.kwargs.get('status')
        return Booking.objects.filter(status=status).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.kwargs.get('status')
        context['status'] = status
        context['title'] = f"{status.title()} Bookings"
        return context

@login_required
def manage_bookings(request):
    if not request.user.is_superuser:
        return redirect('home')
        
    pending_bookings = Booking.objects.filter(status='pending').order_by('created_at')
    return render(request, 'main_app/manage_bookings.html', {
        'pending_bookings': pending_bookings,
    })

@login_required
@user_passes_test(is_superuser)
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'pending':
        booking.status = 'approved'
        booking.save()
        
        # Create notification for user
        Notification.objects.create(
            recipient=booking.user,
            message=f'Your booking for {booking.package.name} has been approved!',
            booking=booking
        )
        
        messages.success(request, 'Booking approved successfully!')
    return redirect('booking_status_list', status='approved')

@login_required
@user_passes_test(is_superuser)
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'pending':
        booking.status = 'rejected'
        booking.save()
        
        # Create notification for user
        Notification.objects.create(
            recipient=booking.user,
            message=f'Your booking for {booking.package.name} has been rejected.',
            booking=booking
        )
        
        messages.success(request, 'Booking rejected successfully!')
    return redirect('booking_status_list', status='rejected')

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'Notification marked as read.')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        messages.error(request, 'Error marking notification as read.')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))