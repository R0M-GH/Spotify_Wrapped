from django.urls import path

from . import views

urlpatterns = [

	path('', views.welcome, name='welcome'),
	path('login/', views.user_login, name='user_login'),

	path('home/', views.home, name='home'),

	path('index/', views.index, name='index-page'),
	path('contact/', views.contact, name='contact'),

	#path('', views.user_login, name='user-login'),
	path('signup/', views.register, name='registration'),
	path('forgot-password/', views.forgot_password, name='forgot-password'),
	path('accountpage/', views.accountpage, name='account-page'),
	path('delete_account/', views.delete_account, name='delete_account'),
	path('spotify_logout/', views.relink_spotify_account, name='spotify_logout'),
	path('summary/', views.summary, name='summary'),
	path('artists-constellation/<int:page>/', views.artist_constellation, name='artist-constellation'),
	path('genre-nebula/<int:page>/', views.genre_nebula, name='genre-nebula'),
	path('stellar-hits/<int:page>/', views.stellar_hits, name='stellar-hits'),
	path('wrapperStart/', views.wrapperStart, name='game'),
	path('game/', views.game, name='game'),
	path('newwrapper/', views.newwrapper, name='game'),
	# path('accountpage/', views.account, name='game'),
	path('welcome/', views.welcome, name='welcome'),
	path('library/', views.library, name='library'),
	path('spotify/login/', views.spotify_login, name='spotify_login'),
	path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
	path('welcome/', views.welcome, name='welcome'),
	path('wrapper/', views.wrapper, name='welcome'),
	path('GenreNebulas/', views.GenreNebulas, name='welcome'),
	path('GenreNebulas2/', views.GenreNebulas2, name='welcome'),
	path('StellarHits/', views.StellarHits, name='welcome'),
	path('StellarHits2/', views.StellarHits2, name='welcome'),
	path('ConstellationArtists/', views.ConstellationArtists, name='welcome'),
	path('ConstellationArtists2/', views.ConstellationArtists2, name='welcome'),
	path('wrapper2/', views.wrapper2, name='welcome'),
	path('contact/', views.contact, name='contact'),
	path('summary/', views.summary, name='summary'),
	path('summary2/', views.summary2, name='summary2'),

	path('api/make-wrapped/<str:time_range>/<int:limit>/', views.make_wrapped, name='make-wrapped'),
	path('api/get-wrapped/<str:dt>/<str:time_range>/', views.get_wrapped, name='get-wrapped'),
	path('api/get-wrapped/<str:dt>/<str:time_range>/', views.get_wrapped, name='get-wrapped'),

	# TEMPORARY (for testing)
	path('api/make-wrapped/', views.make_wrapped, name='make_wrapped'),
]
