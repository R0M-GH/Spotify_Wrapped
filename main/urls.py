from django.urls import path
from . import views

app_name = 'main'  # Add this line to define the namespace

urlpatterns = [
	path('', views.login, name='login'),
	path('index/', views.index, name='index-page'),
	path('home/', views.home, name='home-page'),
	path('signup/', views.register, name='registration'),
	path('spotify/login/', views.spotify_login, name='spotify_login'),
	path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
	path('home', views.home, name='home'),
	path('summary/',views.summary, name='summary'),
	path('ConstellationArtists/', views.ConstellationArtists, name='ConstellationArtists/'),
	path('ConstellationArtists2/', views.ConstellationArtists2, name='ConstellationArtists2/'),
	path('GenreNebulas/', views.GenreNebulas, name='GenreNebulas/'),
	path('GenreNebulas2/', views.GenreNebulas2, name='GenreNebulas2/'),
	path('StellarHits/', views.StellarHits, name='StellarHits/'),
	path('StellarHits2/', views.StellarHits2, name='StellarHits2/'),

	path('game/', views.game_page, name='game_page'),
	path('welcome/', views.welcome, name='welcome'),
	path('library/', views.library_page, name='library_page'),
	path('contact/', views.contact, name='contact'),
	path('summary/', views.summary, name='summary'),

	path('accountpage/', views.accountpage, name='accountpage'),
	path('newwrapper/', views.newwrapper, name='newwrapper'),

	path('wrapper/', views.wrapper_page, name='wrapper'),

	path('wrapper2/', views.wrapper2, name='wrapper2'),
	path('index.html/api/<str:time_range>/', views.spotify_data, name='spotify_data'),
	path('index.html/api/<str:request>/', views.llama_request, name='llama_request'),
]
