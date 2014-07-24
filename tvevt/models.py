# -*- coding: utf-8 -*-
from datetime import date

from django.contrib.auth.models import AbstractUser, UserManager
#from django.contrib.auth.models import User as User_Default
from django.db import models



genders = (
    ('', ''),
    ('male', 'Male'),
    ('female', 'Female'),
)


class CustomUserManager(UserManager):

    def create_user(self, username, 
                    vk_user_id=None, fb_user_id=None,
                    gender=None, birth_date=None, 
                    email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        
        
        email = UserManager.normalize_email(email)
        user = self.model(username=username, 
                          vk_user_id=vk_user_id,
                          fb_user_id=fb_user_id,           
                          gender=gender,
                          birth_date=birth_date,
                          email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user


    



class User(AbstractUser):
    vk_user_id = models.PositiveIntegerField(null=True, default=None, blank=True)
    fb_user_id = models.PositiveIntegerField(null=True, default=None, blank=True)
    
    gender = models.CharField(max_length=6, choices=genders, default='', blank=True)
    birth_date = models.DateField(null=True, default=None, blank=True)

    objects = CustomUserManager()
    backend = 'django.contrib.auth.backends.ModelBackend'
    
    
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            my_birthday = date(today.year, self.birth_date.month, self.birth_date.day)
            if today < my_birthday:
                age = age - 1
    
            return age
        
        else:
            return None
    
    
    

        