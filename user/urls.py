from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('home/',views.index),
    path('product/',views.product),
    path('about/',views.about),
    path('contact/',views.contact),
    path('faqs/',views.faqs),
    path('register/',views.register),
    path('login/',views.login),
    path('logout/',views.logout),
    path('cart/',views.cart),
    path('history/',views.orderhistory),
    path('profile/',views.myprofile),
    path('showcart/',views.showcart),
    path('productcart/', views.cartforproduct),
    path('order/', views.order),
    path('portfolio/', views.portfolio),
]