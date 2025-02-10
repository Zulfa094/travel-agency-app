from django.contrib import admin
from .models import Destination, Package, Booking
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'


# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_role')

#     def profile_role(self, obj):
#         return obj.profile.role
#     profile_role.short_description = 'Role'

#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User)

admin.site.register(Destination)
admin.site.register(Package)
admin.site.register(Booking)