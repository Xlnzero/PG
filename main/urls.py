from django.urls import path, re_path, register_converter
from . import views
from django.urls import path
from django.urls import path








urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('pam/', views.pam, name='pam'),
    path('aks/', views.aks, name='aks'),
    path('obj/', views.obj, name='obj'),
    path('vid/', views.vid, name='vid'),
    path('cat/', views.cat, name='cat'),
    path('model/', views.model, name='model'),
    path('about_mo/', views.about_mo, name='about_mo'),






    path('<str:category>_model/', views.dynamic_model, name='dynamic_model'),
    path('update_od_model/', views.update_od_model, name='update_od_model'),


    path('contact/', views.contact_view, name='contact'),


    path('<str:category>_gal/', views.dynamic_gallery, name='dynamic_gallery'),





    ]

