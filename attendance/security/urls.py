from django.urls import path
from . import views

urlpatterns=[
    path('',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/',views.register,name='register'),
    path('user_guard/',views.user_guard,name='user_guard'),
    path('upload_selfie/',views.upload_selfie,name='upload_selfie'),
    path('guard-details/', views.admin_guard_details, name='admin_guard_details'),
]