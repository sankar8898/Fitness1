from django.urls import path
from . import views

urlpatterns = [
    path('classes/', views.list_classes, name='list_classes'),
    path('book/', views.book_class, name='book_class'),
    path('bookings/', views.list_bookings_by_email, name='list_bookings_by_email'),
]
