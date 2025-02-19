from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('', views.Home.as_view(), name='home'),  
    path('login/', auth_views.LoginView.as_view(template_name='accounts/templates/registration/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),


    # CBV's for Create, Update, Delete Package
    path('packages/create/', views.PackageCreate.as_view(), name='package_create'),
    path('packages/<int:pk>/update/', views.PackageUpdate.as_view(), name='package_update'),
    path('packages/<int:pk>/delete/', views.PackageDelete.as_view(), name='package_delete'),
    path('packages/<int:pk>/', views.PackageDetail.as_view(), name='package_detail'),
    path('packages/', views.PackageList.as_view(), name='package_list'),

        # CBV's for Create, Update, Delete Destination
    path('destinations/create/', views.DestinationCreate.as_view(), name='destination_create'),
    path('destinations/<int:pk>/update/', views.DestinationUpdate.as_view(), name='destination_update'),
    path('destinations/<int:pk>/delete/', views.DestinationDelete.as_view(), name='destination_delete'),
    path('destinations/<int:pk>/', views.DestinationDetail.as_view(), name='destination_detail'),
    path('destinations/', views.DestinationList.as_view(), name='destination_list'),

    path('bookings/create/<int:package_pk>/', views.BookingCreate.as_view(), name='booking_create'),
    path('bookings/', views.BookingList.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', views.BookingDetail.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update/', views.BookingUpdate.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', views.BookingDelete.as_view(), name='booking_delete'),
    
    # Booking Management
    path('manage/bookings/', views.manage_bookings, name='manage_bookings'),
    path('bookings/<int:booking_id>/approve/', views.approve_booking, name='approve_booking'),
    path('bookings/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('bookings/status/<str:status>/', views.BookingStatusList.as_view(), name='booking_status_list'),
]