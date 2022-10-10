from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')


admin.site.register(Follow)
admin.site.register(User, UserAdmin)
