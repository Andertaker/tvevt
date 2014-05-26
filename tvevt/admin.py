# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib import admin
from models import *

'''
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(Profile, ProfileAdmin)
'''

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        #fields = ('username', 'first_name', 'last_name')
        exclude = ('date_joined', 'last_login', 'groups', 'user_permissions', 'password')


class UserAdmin(admin.ModelAdmin):
    form = UserForm
    
    list_display = ('username', 'last_name', 'first_name', 'birth_date', 'get_age', 'is_staff', 'is_superuser', 'is_active')

    
    
    
admin.site.register(User, UserAdmin)