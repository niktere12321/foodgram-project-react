from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    fields = [
        'email',
        'password',
        'role',
        'username',
        'first_name',
        'last_name',
    ]
    list_display = (
        'pk',
        'username',
        'email',
        'password',
    )
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'user')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
