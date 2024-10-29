from django.urls import path, include
from . import views

urlpatterns = [
	#path('', views.home, name='home-page'),
	path('', views.login, name='login'),
	path('signup', views.register, name='registration'),
	#path('', include('django.contrib.auth.urls')),
	path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
	path('index.html/api/<str:artist_name>/', views.search_artist, name='search_artist'),
	path('index.html/api/<str:request>/', views.llama_request, name='llama_request'),

]
