from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
    path('game/', views.game_page, name='game_page'),
    path('library/', views.library_page, name='library_page'),
    path('info/', views.info_page, name='info_page'),
    path('wrapper/', views.wrapper_page, name='wrapper_page'),
	path('index.html/api/<str:artist_name>/', views.search_artist, name='search_artist'),
	path('index.html/api/<str:request>/', views.llama_request, name='llama_request'),
]
