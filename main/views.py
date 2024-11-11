import base64
import json
import os
import random
import string
import urllib.parse

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI

from .backends import AuthModelBackend
from .forms import LoginForm, RegistrationForm
from .models import CustomUserManager, User


def index(request):
	return render(request, 'index.html')


# @login_required
def home(request):
	return render(request, 'mainTemplates/index.html', {})

def welcome(request):
	return render(request, 'Spotify_Wrapper/index.html')
def game_page(request):
	return render(request, 'Spotify_Wrapper/game.html')


def library_page(request):
	# add library display logic here
	return render(request, 'Spotify_Wrapper/library.html')


def info_page(request):
	if request.method == 'POST':
		# Process info form submission
		return redirect('wrapper_page')
	return render(request, 'Spotify_Wrapper/info.html')


def wrapper_page(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/wrapper.html')

def wrapper2(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/wrapper2.html')

def ConstellationArtists(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/ConstellationArtists.html')

def ConstellationArtists2(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/ConstellationArtists2.html')

def GenreNebulas(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/GenreNebulas.html')

def GenreNebulas2(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/GenreNebulas2.html')

def StellarHits(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/StellarHits.html')

def StellarHits2(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/StellarHits2.html')
def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password1 = form.cleaned_data['password1']

			# Check if username already exists in User model
			if User.objects.filter(username=username).exists():
				return render(request, 'registration/registration.html', {"form": form, 'error': True})

			# Creates users
			user = CustomUserManager.create_user(username=username, password=password1)
			return redirect("login")
	else:
		form = RegistrationForm()
	return render(request, 'registration/registration.html', {"form": form})


def login(request):
	request.session.flush()
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = AuthModelBackend.authenticate(username, password)
		if user is not None:
			request.session['username'] = username

			# # Replace this with actual Spotify API logic to get tokens
			# spotify_access_token = 'obtained_access_token'
			# spotify_refresh_token = 'obtained_refresh_token'
			#
			# # Set the tokens on the user model
			# user.spotify_access_token = spotify_access_token
			# user.spotify_refresh_token = spotify_refresh_token
			# user.save()  # Save to database

			# login(request, user)
			return redirect("home_page")
		else:
			form = LoginForm()
			return render(request, 'registration/login.html', {'form': form, 'error': True})
	else:
		form = LoginForm()
	return render(request, 'registration/login.html', {'form': form})


def generate_random_state(length):
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def spotify_login(request):
	state = generate_random_state(16)
	scope = 'user-read-private user-read-email'
	auth_url = 'https://accounts.spotify.com/authorize?'

	query_params = {
		'response_type': 'code',
		'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
		'scope': scope,
		'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
		'state': state,
	}

	url = auth_url + urllib.parse.urlencode(query_params)

	return redirect(url)


def spotify_callback(request):
	code = request.GET.get('code')
	state = request.GET.get('state')
	error = request.GET.get('error')

	auth_string = os.getenv('SPOTIFY_CLIENT_ID') + ":" + os.getenv('SPOTIFY_CLIENT_SECRET')
	auth_bytes = auth_string.encode("utf-8")
	auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

	if error:
		return error
	if not code:
		return JsonResponse({'error': 'Invalid code'}, status=400)

	# Exchange code for an access token
	token_url = 'https://accounts.spotify.com/api/token'
	body = {
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
		'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
		'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
	}
	header = {
		'Authorization': 'Basic ' + auth_base64,
		'Content-Type': 'application/x-www-form-urlencoded',
	}

	response = requests.post(token_url, data=body, headers=header)
	response_data = response.json()

	if 'access_token' in response_data:
		access_token = response_data['access_token']
		refresh_token = response_data['refresh_token']

		# # Store tokens in session (or database)
		# request.session['access_token'] = access_token
		# request.session['refresh_token'] = refresh_token

		# Assuming user session has 'username' set from login view
		username = request.session.get('username')
		if username:
			user = User.objects.get(username=username)
			user.spotify_access_token = access_token
			user.spotify_refresh_token = refresh_token
			user.save()  # Save tokens to the user model

		return redirect("home")
		# return JsonResponse({
		# 	'message': 'Authorization successful',
		# 	'access_token': access_token,
		# 	'refresh_token': refresh_token
		# })
	else:
		return JsonResponse({'error': 'Failed to obtain token'}, status=400)


@csrf_exempt
@login_required
def get_token():
	load_dotenv()
	auth_string = os.getenv('SPOTIFY_CLIENT_ID') + ":" + os.getenv('SPOTIFY_CLIENT_SECRET')
	auth_bytes = auth_string.encode("utf-8")
	auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
	url = "https://accounts.spotify.com/api/token"
	headers = {"Authorization": "Basic " + auth_base64, "Content-Type": "application/x-www-form-urlencoded"}
	data = {"grant_type": "client_credentials"}
	result = requests.post(url, headers=headers, data=data)
	json_result = json.loads(result.content)
	return json_result["access_token"]


@csrf_exempt
@login_required
def spotify_data(request, time_range="medium_term"):
	access_token = User.objects.get(user=request.user).spotify_access_token

	headers = {"Authorization": f"Bearer {access_token}"}

	user_top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"
	user_top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"

	top_tracks_response = requests.get(user_top_tracks_url, headers=headers)
	top_artists_response = requests.get(user_top_artists_url, headers=headers)

	if top_tracks_response.status_code == 200 and top_artists_response.status_code == 200:
		data = {
			"top_tracks": top_tracks_response.json(),
			"top_artists": top_artists_response.json(),
			"time_range": time_range
		}
		return JsonResponse(data)
	else:
		return JsonResponse({"error": "Failed to retrieve data from Spotify"}, status=400)


@csrf_exempt
@login_required
def llama_request(token, request):
	client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv('OPENAI_API_KEY'))
	completion = client.chat.completions.create(model="meta/llama-3.1-405b-instruct",
	                                            messages=[{"role": "user", "content": f"{request}"}], temperature=0.2,
	                                            top_p=0.7, max_tokens=1024, stream=True)
	info = ''
	for chunk in completion:
		if chunk.choices[0].delta.content:
			info += chunk.choices[0].delta.content
	return JsonResponse({'info': info})
