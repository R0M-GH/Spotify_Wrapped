from django.urls import path

from . import views

urlpatterns = [

	path('', views.welcome, name='welcome'),
	path('login/', views.user_login, name='user_login'),

	path('home/', views.home, name='home'),

	path('index/', views.index, name='index-page'),
	path('contact/', views.contact, name='contact'),

	path('', views.user_login, name='user-login'),
	path('signup/', views.register, name='registration'),
	path('forgot-password/', views.forgot_password, name='forgot-password'),
	path('account-page/', views.accountpage, name='account-page'),

	path('summary/', views.summary, name='summary'),
	path('artists-constellation/<int:page>/', views.artist_constellation, name='artist-constellation'),
	path('genre-nebula/<int:page>/', views.genre_nebula, name='genre-nebula'),
	path('stellar-hits/<int:page>/', views.stellar_hits, name='stellar-hits'),

	path('game/', views.game, name='game'),
	path('welcome/', views.welcome, name='welcome'),
	path('library/', views.library, name='library'),

	path('spotify/login/', views.spotify_login, name='spotify_login'),
	path('spotify/callback/', views.spotify_callback, name='spotify_callback'),


	path('game/', views.game_page, name='game_page'),
	path('welcome/', views.welcome, name='welcome'),
	path('library/', views.library_page, name='library_page'),
	path('contact/', views.contact, name='contact'),
	path('summary/', views.summary, name='summary'),
path('summary2/', views.summary2, name='summary2'),

	path('api/make-wrapped/<str:time_range>/<int:limit>/', views.make_wrapped, name='make-wrapped'),
	path('api/make-wrapped/<str:dt>/', views.get_wrapped, name='get-wrapped'),
	path('api/<str:msg>/<str:data>/', views.llama_request, name='llama_request'),


	# TEMPORARY (for testing)
	path('api/make-wrapped/', views.make_wrapped, name='make_wrapped'),
]
