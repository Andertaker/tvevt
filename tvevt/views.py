# -*- coding: utf-8 -*-
import json
from datetime import date
from httplib import HTTPConnection, HTTPSConnection

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from oauthlib.oauth2 import WebApplicationClient
#from django.contrib.auth.models import User

from rest_framework import generics
#from rest_framework import filters
#from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from tvevt.serializers import UserSerializer
from models import User
from settings import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from settings import VK_APP_ID, VK_APP_SECRET




class CurrentUserView(generics.RetrieveUpdateAPIView):
    #model = User
    serializer_class = UserSerializer
    #lookup_field = None
    
    queryset = User.objects.all()

    def retrieve(self, request, format="json"):
        user = self.request.user
        if user.is_anonymous():
            return Response({"status": "error"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return Response({"status": "error"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        



class UsersView(generics.RetrieveAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    model = User
    serializer_class = UserSerializer
    
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = ('age',)



class UsersByAgeView(generics.ListAPIView):
    def get(self, request, format="json"):
        queryset = User.objects.all()
        age = self.request.GET.get('age', 0)
        age = int(age)
        print age
        

        if age > 0:
            today = date.today()
            max_date = date((today.year - age), today.month, today.day)
            min_date = date((today.year - age - 1), today.month, today.day)

            queryset = queryset.filter(birth_date__gt=min_date, birth_date__lt=max_date)

        ids = []
        for u in queryset:
            ids.append(u.id)

        return Response(ids)





'''
Аутентификация в приложении через соц.сети ВКонтакте, Facebook,
 авторизация API по протоколу OAuth 2.0.
 При первой аутентификации из соц. сети подгружаются имя, фамилия, пол и возраст.
 Данные значения используются значениями по умолчанию для полей локальной БД.

'''

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

def login_view(request):
    client = WebApplicationClient(VK_APP_ID)
    vk_uri = client.prepare_request_uri('https://oauth.vk.com/authorize',
                           scope=['notify'],
                           redirect_uri='http://localhost/vk_register',
                           v='5.17')

    context = {'vk_uri': vk_uri}
    
    '''
    На FaceBook времени не хватило вообщем
    
    client = WebApplicationClient(FACEBOOK_APP_ID)
    fb_uri = client.prepare_request_uri('https://www.facebook.com/dialog/oauth',
                           redirect_uri='http://localhost/fb_register')

    '''

    context = {'vk_uri': vk_uri, 'fb_uri': '#'}
    return render(request, 'tvevt/login.html', context)



def fb_register(request):
    pass



def vk_register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_detail'))
    
    code = request.GET.get('code', '')
    if code == '':
        raise ValueError(u"Bad response")
        #return render(request, 'tvevt/fail.html', context)
    

    client = WebApplicationClient(VK_APP_ID)
    uri = client.prepare_request_uri('https://oauth.vk.com/access_token',
                               client_secret=VK_APP_SECRET,
                               code=code,
                               redirect_uri='http://localhost/vk_register')

    h = HTTPSConnection("vk.com")
    h.request('GET', uri)
    r = h.getresponse()
    body = r.read()

    r = json.loads(body)
    user_id = r["user_id"]
    access_token = r["access_token"]

    uri = client.prepare_request_uri('https://api.vk.com/method/users.get',
                               user_id=user_id,
                               access_token=access_token,
                               fields='sex,bdate')

    h.request('GET', uri)
    r = h.getresponse()
    body = r.read()
    r = json.loads(body)
    user = r["response"][0]
    
    
    if user["uid"] <=0:
        raise ValueError(u"Bad uid value")
    
    list = User.objects.filter(vk_user_id=user["uid"])
    if len(list) == 1:
        u = list[0]
        login(request, u)
        return HttpResponseRedirect(reverse('user_detail'))
    
    else:
        "Если пользователя нет, то регистрируем его"
        
        username = "vk_%d" % user["uid"]
        l = user["bdate"].split('.')
        year = int(l[2])
        month = int(l[1])
        day = int(l[0])
        user["bdate"] = date(year, month, day)
        
        if user["sex"] == 2:
            user["sex"] = "male"
        elif user["sex"] == 1:
            user["sex"] = "female"
        else:
            user["sex"] == ''
    
        u = User(username=username,
                 vk_user_id=user["uid"],
                  first_name=user["first_name"], last_name=user["last_name"],
                  gender=user["sex"], birth_date=user["bdate"])
        u.save()
 
        login(request, u)
        return render(request, 'tvevt/success.html')




