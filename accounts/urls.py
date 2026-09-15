from django.urls import path
from . import views


urlpatterns=[
    path('',views.user_dashboard,name='user_dashboard'),
    path('profile/',views.user_profile,name='user_profile'),
    path('account_settings/',views.accountSettings,name='account_settings'),
    path('signin/',views.createUser,name='signin'),
    path('login/',views.Userlogin,name='login'),
    path('logout_confirmation/',views.logout_confirmation,name='logout_confirmation'),
    path('delete_account/',views.delete_account,name='delete_account'),
    path('editProfile/',views.editProfile,name='editProfile'),
    path('address/',views.address,name='address'),
    path('add_address/',views.addAddress,name='add_address'),
    path('edit_address/<str:pk>/',views.editAddress,name='edit_address'),
    path('delete_address/<str:pk>/',views.deleteAddress,name='delete_address'),
]

