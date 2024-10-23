from django.urls import path, include
from . import views

urlpatterns = [
	#path('', views.home, name='home-page'),
	path('', views.login, name='login'),
	#path('', include('django.contrib.auth.urls')),
	path('index.html/api/<str:artist_name>/', views.search_artist, name='search_artist'),
	path('index.html/api/<str:request>/', views.llama_request, name='llama_request'),

]
