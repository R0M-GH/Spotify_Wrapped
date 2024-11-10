from django.urls import path
from . import views

urlpatterns = [
	path('', views.login, name='login'),
	path('index', views.index, name='index-page'),
	path('signup', views.register, name='registration'),
	path('spotify/login/', views.spotify_login, name='spotify_login'),
	path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
	path('home', views.home, name='home'),
	path('game/', views.game_page, name='game_page'),
	path('library/', views.library_page, name='library_page'),
	path('info/', views.info_page, name='info_page'),
	path('wrapper/', views.wrapper_page, name='wrapper_page'),
	path('index.html/api/<str:time_range>/', views.spotify_data, name='spotify_data'),
	path('index.html/api/<str:request>/', views.llama_request, name='llama_request'),
]
