import base64
import json
import os
import random
import string
import urllib.parse

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

from Spotify_Wrapped import settings
from .forms import LoginForm, RegistrationForm, ForgetForm
from .models import User, Wraps


def index(request):
	return render(request, 'mainTemplates/index.html')


def welcome(request):
	return render(request, 'Spotify_Wrapper/welcome.html')


def summary(request):
	return render(request, 'Spotify_Wrapper/summary.html')


def accountpage(request):
	return render(request, 'Spotify_Wrapper/accountpage.html')


def contact(request):
	return render(request, 'Spotify_Wrapper/contact.html')


def newwrapper(request):
	return render(request, 'Spotify_Wrapper/newwrapper.html')


@login_required
def home(request):
	return render(request, 'mainTemplates/index.html', {})


def game_page(request):
	return render(request, 'Spotify_Wrapper/game.html')


def library_page(request):
	# add library display logic here
	return render(request, 'Spotify_Wrapper/library.html')


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
			birthday = form.cleaned_data['birthday']

			# Check if username already exists in User model
			if User.objects.filter(username=username).exists():
				return render(request, 'registration/registration.html', {"form": form, 'error': True})

			# Creates users
			user = User.objects.create_user(username=username, password=password1)
			user.birthday = birthday
			user.save()
			return redirect("user_login")
	else:
		form = RegistrationForm()
	return render(request, 'registration/registration.html', {"form": form})


def user_login(request):
	request.session.flush()
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		# user = AuthModelBackend.authenticate(request, username, password)
		user = authenticate(request, username=username, password=password)
		if user is not None:
			request.session['username'] = username

			login(request, user)
			return redirect("spotify_login")

		else:
			form = LoginForm()
			return render(request, 'registration/login.html', {'form': form, 'error': True})
	else:
		form = LoginForm()
	return render(request, 'registration/login.html', {'form': form})


def forgot_password(request):
	if request.method == 'POST':
		username = request.POST['username']
		security_answer = request.POST['security_answer']
		new_password1 = request.POST['new_password1']
		new_password2 = request.POST['new_password2']

		if new_password1 != new_password2:
			return render(request, 'registration/Forget.html', {'error': 'Passwords do not match'})

		try:
			user = User.objects.get(username=username)

			if str(user.birthday) == str(security_answer):  # Check if birthday matches
				user.password = make_password(new_password1)
				user.save()
				return redirect('user_login')
			else:
				form = ForgetForm()
				return render(request, 'registration/Forget.html', {'form': form, 'error': 'Birthday does not match'})

		except User.DoesNotExist:
			form = ForgetForm()
			return render(request, 'registration/Forget.html', {'form': form, 'error': True})
	else:
		form = ForgetForm()
	return render(request, 'registration/forget.html', {'form': form})


def generate_random_state(length):
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def spotify_login(request):
	state = generate_random_state(16)
	scope = 'user-read-private user-read-email user-top-read streaming user-modify-playback-state'
	auth_url = 'https://accounts.spotify.com/authorize?'

	query_params = {
		'response_type': 'code',

		# 'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
		'client_id': settings.SPOTIFY_CLIENT_ID,

		'scope': scope,

		# 'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
		'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
		'state': state,
	}

	url = auth_url + urllib.parse.urlencode(query_params)

	return redirect(url)


def spotify_callback(request):
	code = request.GET.get('code')
	state = request.GET.get('state')
	error = request.GET.get('error')

	# auth_string = os.getenv('SPOTIFY_CLIENT_ID') + ":" + os.getenv('SPOTIFY_CLIENT_SECRET')
	auth_string = settings.SPOTIFY_CLIENT_ID + ":" + settings.SPOTIFY_CLIENT_SECRET

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

		# 'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
		'redirect_uri': settings.SPOTIFY_REDIRECT_URI,

		# 'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
		'client_id': settings.SPOTIFY_CLIENT_ID,

		# 'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
		'client_secret': settings.SPOTIFY_CLIENT_SECRET,
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

		# Assuming user session has 'username' set from login view
		username = request.session.get('username')
		if username:
			user = User.objects.get(username=username)
			user.spotify_access_token = access_token
			user.spotify_refresh_token = refresh_token
			user.save()  # Save tokens to the user model

		return redirect("home")
	else:
		return JsonResponse({'error': 'Failed to obtain token'}, status=400)


def refresh_spotify_token(user):
	refresh_token = user.spotify_refresh_token

	response = requests.post('https://accounts.spotify.com/api/token', data={
		'grant_type': 'refresh_token',
		'refresh_token': refresh_token,
		'client_id': 'your_client_id',
		'client_secret': 'your_client_secret',
	})

	if response.status_code != 200:
		tokens = response.json()
		access_token = tokens['access_token']
		user.spotify_access_token = access_token
		user.save()
		return access_token
	else:
		return None


@csrf_exempt
@login_required
def spotify_data(request, time_range='medium_term'):
	user = User.objects.get(username=request.user.username)
	endpoint = 'https://api.spotify.com/v1/me/'

	if not user.spotify_access_token:
		return JsonResponse({'error': 'User is not authenticated with Spotify.'}, status=401)

	headers = {'Authorization': f'Bearer {user.spotify_access_token}'}
	response = requests.get(endpoint, headers=headers)

	if response.status_code == 401:
		access_token = refresh_spotify_token(user)
		if not access_token:
			return JsonResponse({'error': 'Failed to refresh access token.'}, status=400)
		user.spotify_access_token = access_token
		user.save()

	top_tracks_response = requests.get(f'{endpoint}/top/tracks?limit=5&time_range={time_range}', headers=headers)
	top_artists_response = requests.get(f'{endpoint}/top/artists?limit=5&time_range={time_range}', headers=headers)

	if top_tracks_response.status_code != 200 and top_artists_response.status_code != 200:
		return JsonResponse({'error': 'Failed to retrieve data from Spotify'}, status=400)

	data = {
		'time_range': time_range,
		'top_tracks': top_tracks_response.json(),
		'top_artists': top_artists_response.json(),
	}

	json_wrapped_data = json.dumps(data)
	wrap = Wraps(username=user.username, wrap_json=json_wrapped_data)
	wrap.save()

	# THIS IS FOR TESTING (DELETE TWO LINES BELOW DEPENDING ON IMPLEMENTATION)
	return HttpResponse(wrap.wrap_json, content_type='application/json')


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


@login_required
def playback(request):
	# Fetch the user's Spotify access token
	username = request.session.get('username')
	user = User.objects.get(username=username)
	access_token = user.spotify_access_token

	# Fetch user's top tracks from Spotify API
	headers = {"Authorization": f"Bearer {access_token}"}
	response = requests.get(
		"https://api.spotify.com/v1/me/top/tracks?limit=10",
		headers=headers,
	)

	if response.status_code == 200:
		top_tracks = response.json()['items']  # Extract top tracks
	else:
		top_tracks = []  # Handle error or no tracks found

	# Pass track information (URIs, names, etc.) to the template
	return render(request, 'mainTemplates/playback.html', {'access_token': access_token, 'top_tracks': top_tracks})
