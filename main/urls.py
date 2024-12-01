from django.urls import path

from . import views

urlpatterns = [
	path('', views.welcome, name='welcome'),
	path('login/', views.user_login, name='user_login'),
	path('signup/', views.register, name='registration'),
	path('forgot-password/', views.forgot_password, name='forgot-password'),
	path('accountpage/', views.accountpage, name='account-page'),
	path('delete_account/', views.delete_account, name='delete_account'),

	path('spotify/login/', views.spotify_login, name='spotify_login'),
	path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
	path('spotify_logout/', views.relink_spotify_account, name='spotify_logout'),

	path('home/', views.home, name='home'),

	path('index/', views.index, name='index-page'),
	path('contact/', views.contact, name='contact'),

	path('welcome/', views.welcome, name='welcome'),
	path('game/', views.game, name='game'),
	path('library/', views.library, name='library'),

	path('newwrapper/', views.newwrapper, name='new_wrapped'),
	path('wrapperStart/<str:dt>/', views.wrapperStart, name='wrapper-start'),
	path('wrapper/<str:dt>/', views.wrapper, name='wrapped'),
	path('GenreNebulas/<str:dt>/', views.GenreNebulas, name='genre_nebulas'),
	path('StellarHits/<str:dt>/', views.StellarHits, name='stellar_hits'),
	path('ConstellationArtists/<str:dt>/', views.ConstellationArtists, name='artist_constellation'),
	path('AstroAI/<str:dt>/', views.AstroAI, name='astro-ai'),
	path('summary/<str:dt>/', views.summary, name='summary'),

	path('api/make-wrapped/<str:time_range>/<int:limit>/', views.make_wrapped, name='make-wrapped'),
	path('api/get-wrapped/<str:dt>/', views.get_wrapped, name='get-wrapped'),
	path('api/delete-wrapped/<str:dt>/', views.delete_wrapped, name='delete-wrapped'),
	path('api/get-game-info/', views.get_game_info, name='game-info'),
]
