from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Destination, Package, Booking
from .forms import SignupForm, BookingForm # Form Name SignupForm
from django.contrib.auth.decorators import login_required # Import Decorator
from django.contrib.auth.mixins import LoginRequiredMixin # Import Mixin
from django.contrib.auth.views import LoginView


# Guest Views
class Home(LoginView):
    template_name = 'home.html'
    redirect_authenticated_user = True # If the user its authenticated goes to homepage
    # def get_success_url(self):   # You need to create it for the login to work
    #     return reverse_lazy('main_app:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.all()  # Pass all packages
        context['destinations'] = Destination.objects.all() # pass all destinations
        return context


def about(request):
    return render(request, 'about.html')


def signup(request):
    error_message= ''
    if request.method== 'POST':
        form =SignupForm(request.POST) # Form Name SignupForm
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Reditect the user to the home
        else:
            error_message = 'Invalid sign up - try again'

    form = SignupForm() # Form Name SignupForm
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

# Admin Views
class PackageCreate(LoginRequiredMixin, CreateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations'] # add the destinations in the fields to render the form
    success_url = reverse_lazy('main_app:home')

class PackageUpdate(LoginRequiredMixin, UpdateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    success_url = reverse_lazy('main_app:home')

class PackageDelete(LoginRequiredMixin, DeleteView):
    model = Package
    success_url = reverse_lazy('main_app:home')
    template_name = 'package/package_confirm_delete.html'

class DestinationCreate(LoginRequiredMixin, CreateView):
    model = Destination
    fields = ['name', 'description']
    success_url = reverse_lazy('main_app:home')

class DestinationUpdate(LoginRequiredMixin, UpdateView):
    model = Destination
    fields = ['name', 'description']
    success_url = reverse_lazy('main_app:home')

class DestinationDelete(LoginRequiredMixin, DeleteView):
    model = Destination
    success_url = reverse_lazy('main_app:home')

class PackageDetail(DetailView):
    model = Package
    template_name = 'package/detail.html'

class DestinationDetail(DetailView):
    model = Destination
    template_name = 'destination/detail.html'

# Customer View
class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking/form.html'  # Specify the template

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associate the logged-in user
        return super().form_valid(form)
    
    success_url = reverse_lazy('home')

class BookingDetail(LoginRequiredMixin, DetailView):
    model= Booking
    template_name= 'booking/detail.html'

class BookingDelete(LoginRequiredMixin, DeleteView):
    model= Booking
    template_name= 'booking/booking_confirm_delete.html'
    success_url = reverse_lazy('home')