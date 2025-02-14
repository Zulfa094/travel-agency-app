from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
# from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Destination, Package, Booking
# from .forms import BookingForm 
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def is_superuser(user):
    return user.is_authenticated and user.is_superuser

class Home(ListView):
    model = Package
    template_name = 'home.html'
    context_object_name = 'packages'

def about(request):
    return render(request, 'about.html')

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)
#             next_url = request.POST.get('next', 'main_app:home')
#             return redirect(next_url)
#         else:
#             messages.error(request, 'Invalid username or password.')
    
#     return render(request, 'home.html')

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





class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


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
    

# class PackageList(ListView):
#     model = Package
#     template_name = 'package_list.html'


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


class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['booking_date', 'number_of_guests', 'contact_email', 'contact_phone']
    template_name = 'main_app/booking_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination_id = self.kwargs.get('destination_id')
        context['destination'] = Destination.objects.get(pk=destination_id)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        destination_id = self.kwargs.get('destination_id')
        form.instance.destination = Destination.objects.get(pk=destination_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('booking_detail', kwargs={'pk': self.object.pk})

class BookingDetail(LoginRequiredMixin, DetailView):
    model= Booking
    template_name= 'booking_detail.html'

class BookingDelete(LoginRequiredMixin, DeleteView):
    model= Booking
    def get_success_url(self):
       return redirect('home')
    template_name= 'booking_confirm_delete.html'