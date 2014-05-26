# -*- coding: utf-8 -*-
import settings
from django.conf.urls import patterns, include, url
#from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from django.contrib import admin
admin.autodiscover()

import views
from models import User


apipatterns = patterns('',
    url('^user$', views.CurrentUserView.as_view(), name="user_detail"),
    url('^users/(?P<pk>\d+)$', views.UsersView.as_view()),
    url('^users$', views.UsersByAgeView.as_view()),   
                       
)
#apipatterns = format_suffix_patterns(apipatterns, allowed=['json'])


urlpatterns = patterns('',
    #url(r'^api/', include(router.urls)),
    url(r'^api/', include(apipatterns)),
    
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.


    
    
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    url(r'^$', views.login_view),
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^vk_register', views.vk_register),

)






if settings.DEBUG:
    urlpatterns = patterns('',
                           
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),     
                                  
    url(r'', include('django.contrib.staticfiles.urls')),
    
) + urlpatterns







