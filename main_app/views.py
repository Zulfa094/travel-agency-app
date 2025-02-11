from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
# from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Destination, Package, Booking
from .forms import BookingForm 
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.views import LoginView


class Home(LoginView):
    template_name = 'home.html'
    # redirect_authenticated_user = True
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.all()
        context['destinations'] = Destination.objects.all()
        return context

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
            return redirect('main_app:home')  
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)


class DestinationCreate(LoginRequiredMixin, CreateView):
    model = Destination
    fields = ['name', 'description']
    def get_success_url(self):
        return redirect('main_app:home')

class DestinationUpdate(LoginRequiredMixin, UpdateView):
    model = Destination
    fields = ['name', 'description']
    def get_success_url(self):
        return redirect('main_app:destination_detail', pk=self.object.pk)

class DestinationDelete(LoginRequiredMixin, DeleteView):
   model = Destination
   def get_success_url(self):
       return redirect('main_app:home')
   template_name = 'main_app/destination_confirm_delete.html'


class DestinationDetail(DetailView):
    model = Destination
    template_name = 'main_app/destination_detail.html'


class PackageCreate(LoginRequiredMixin, CreateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    def get_success_url(self):
        return redirect('main_app:home')

class PackageList(ListView):
    model = Package
    template_name = 'main_app/package_list.html'


class PackageUpdate(LoginRequiredMixin, UpdateView):
    model = Package
    fields = ['name', 'description', 'price', 'destinations']
    def get_success_url(self):
        return redirect('main_app:package_detail', pk=self.object.pk)

class PackageDelete(LoginRequiredMixin, DeleteView):
   model = Package
   def get_success_url(self):
       return redirect('main_app:home')
   template_name = 'main_app/package_confirm_delete.html'


class PackageDetail(DetailView):
    model = Package
    template_name = 'main_app/package_detail.html'

# Booking Views (Customer)
class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'main_app/booking_form.html'
    

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect('main_app:booking_detail', pk=self.object.pk)

class BookingDetail(LoginRequiredMixin, DetailView):
    model= Booking
    template_name= 'main_app/booking_detail.html'

class BookingDelete(LoginRequiredMixin, DeleteView):
    model= Booking
    def get_success_url(self):
       return redirect('main_app:home')
    template_name= 'main_app/booking_confirm_delete.html'