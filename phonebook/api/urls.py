from django.urls import path, include
from api.views import ContactList,Register,Login,MarkSpam,SearchName,SearchPhoneNumber

urlpatterns=[
	path('contacts/',ContactList.as_view(),name='ContactList'),
	path('register/',Register.as_view(),name='Register'),
	path('login/',Login.as_view(),name='Login'),
	path('spams/',MarkSpam.as_view(),name='MarkSpam'),
	path('search_by_name/',SearchName.as_view(),name='SearchName'),
	path('search_by_phone_number/',SearchPhoneNumber.as_view(),name='SearchPhoneNumber')
]