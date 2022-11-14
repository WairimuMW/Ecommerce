"""art_dealership URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    # General
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('art/', views.art, name="art"),
    path('contact/', views.contact, name="contact"),
    path('register/', views.register, name="register"),
    path('user_logout/', views.user_logout, name="logout"),
    path('user_login/', views.user_login, name="login"),
    
    # Ecommerce
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
    path('receipt/', views.receipt, name="receipt"),
    
    # Artist
    path('artist_register/', views.artist_register, name="artist_register"),
    # path('artist_login/', views.artist_login, name="artist_login"),
    path('artist_dashboard/', views.artist_dashboard, name="artist_dashboard"),
    path('artist_account/', views.artist_account, name="artist_account"),
    path('artist_settings/', views.artist_settings, name="artist_settings"),
    path('artist_report/', views.artist_report, name="artist_report"),
    
    # Art
    path('create_art/<str:pk>/', views.createArt, name="create_art"),
    path('update_art/<str:pk>/', views.updateArt, name="update_art"),
    path('delete_art/<str:pk>/', views.deleteArt, name="delete_art"),
    
    # Customer
    path('customer_register/', views.customer_register, name="customer_register"),
    # path('customer_login/', views.customer_login, name="customer_login"),
    path('customer_dashboard/', views.customer_dashboard, name="customer_dashboard"),
    path('customer_account/', views.customer_account, name="customer_account"),
    path('customer_settings/', views.customer_settings, name="customer_settings"),
    path('customer_report/', views.customer_report, name="customer_report"),
    
    # Password reset
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="arts/reset_password.html"),
         name="reset_password"),
    
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="arts/password_reset_done.html"), 
         name="password_reset_done"),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="arts/password_reset_form.html"), 
         name="password_reset_confirm"),
    
    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="arts/password_reset_complete.html"), 
         name="password_reset_complete"),
]
