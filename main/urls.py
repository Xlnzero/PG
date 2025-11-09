from django.urls import path, re_path, register_converter
from . import views
from django.urls import path
from django.urls import path








urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('pam/', views.pam, name='pam'),
    path('pam_got/', views.pam_got, name='pam_got'),
    path('aks/', views.aks, name='aks'),

    path('vid/', views.vid, name='vid'),
    path('cat/', views.cat, name='cat'),
    path('model/', views.model, name='model'),
    path('about_mo/', views.about_mo, name='about_mo'),

    path('<str:category>_got_model/', views.pam_got_gallery, name='pam_got_gallery'),
    path('<str:category>_model/', views.pam_render_gallery, name='pam_render_gallery'),

    path('update_od_model/', views.update_od_model, name='update_od_model'),


    path('contact/', views.contact_view, name='contact'),


    path('<str:category>_gal/', views.osn_gallery, name='osn_gallery'),





    ]

