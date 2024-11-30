import base64
import json
import random
import string
import urllib.parse
from datetime import datetime

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
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


@login_required
def summary(request):
	return render(request, 'Spotify_Wrapper/summary.html')


@login_required
def summary2(request):
	return render(request, 'Spotify_Wrapper/summary.html')


@login_required
def accountpage(request):
	username = request.session.get('username')
	wrap_set = Wraps.objects.filter(username=username).order_by('-creation_date')
	wrap_count = wrap_set.count()
	most_recent_wrap = wrap_set.first()
	display_name = User.objects.get(username=username).current_display_name
	if most_recent_wrap:
		most_recent_wrap_date = most_recent_wrap.creation_date
	else:
		most_recent_wrap_date = None
	context = {
		"username": username,
		"display_name": display_name,
		"wrap_count": wrap_count,
		"most_recent_wrap_date": most_recent_wrap_date,
	}
	return render(request, 'Spotify_Wrapper/accountpage.html', context)


@login_required
def contact(request):
	return render(request, 'Spotify_Wrapper/contact.html')


@login_required
def newwrapper(request):
	return render(request, 'Spotify_Wrapper/newwrapper.html')


@login_required
def home(request):
	return render(request, 'mainTemplates/index.html', {})


@login_required
def game(request):
	return render(request, 'Spotify_Wrapper/game.html')


@login_required
def wrapper(request, dt):
	return render(request, 'Spotify_Wrapper/wrapper.html', {'dt': dt})


@login_required
def GenreNebulas(request, dt):
	return render(request, 'Spotify_Wrapper/GenreNebulas.html', {'dt': dt})


@login_required
def StellarHits(request, dt):
	return render(request, 'Spotify_Wrapper/StellarHits.html', {'dt': dt})


@login_required()
def ConstellationArtists(request, dt):
	return render(request, 'Spotify_Wrapper/ConstellationArtists.html', {'dt': dt})


@login_required()
def AstroAI(request, dt):
	return render(request, 'Spotify_Wrapper/AstroAI.html', {'dt': dt})


@login_required
def newwrapper(request):
	return render(request, 'Spotify_Wrapper/newwrapper.html')


@login_required
def wrapperStart(request):
	return render(request, 'Spotify_Wrapper/wrapperStart.html')


# @login_required
# def account(request):
# 	username = request.session.get('username')
# 	wrap_set = Wraps.objects.filter(username=username).order_by('-creation_date')
# 	wrap_count = wrap_set.count()
# 	most_recent_wrap = wrap_set.first()
# 	most_recent_wrap_date = most_recent_wrap.creation_date
# 	context = {
# 		"username": username,
# 		"wrap_count": wrap_count,
# 		"most_recent_wrap_date": most_recent_wrap_date,
# 	}
# 	return render(request, 'Spotify_Wrapper/accountpage.html', context)

@login_required
def library(request):
	username = request.session.get('username')
	wrap_set = Wraps.objects.filter(username=username)
	context = {
		"wrap_set": wrap_set,
	}

	# add library display logic here
	return render(request, 'Spotify_Wrapper/library.html', context)


@login_required
def wrapped_page(request):
	# Load users most recent wrapper info here
	return render(request, 'Spotify_Wrapper/wrapper.html')


def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)

		# Check if form is valid
		if form.is_valid():
			username = form.cleaned_data['username']
			password1 = form.cleaned_data['password1']
			birthday = form.cleaned_data['birthday']

			# Check if username already exists in User model
			if User.objects.filter(username=username).exists():
				# If the username exists, show an error message
				return render(request, 'registration/registration.html', {
					"form": form,
					'error': 'An account with this username already exists.',
				})

			# Create the new user
			user = User.objects.create_user(username=username, password=password1)
			user.birthday = birthday
			user.save()

			# Redirect to the login page
			return redirect("user_login")

		else:
			# If form is invalid, re-render the registration page with form errors
			return render(request, 'registration/registration.html', {
				"form": form,
			})

	else:
		# GET request: render the empty registration form
		form = RegistrationForm()

	return render(request, 'registration/registration.html', {
		"form": form,
	})


def user_login(request):
	request.session.flush()
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
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
		return render(request, 'registration/login.html', {'form': form, 'error': False})


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


def relink_spotify_account(request):
	return render(request, 'Spotify_Wrapper/relink_spotify_account.html', {
		'redirect_url': "http://localhost:8000/spotify/login"  # URL to redirect to after logout
	})


def delete_account(request):
	username = request.session.get('username')
	user = User.objects.get(username=username)
	user.delete_with_wraps()
	return redirect("user_login")


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

			headers = {'Authorization': f'Bearer {access_token}'}
			response = requests.get('https://api.spotify.com/v1/me', headers=headers)
			if response.status_code == 200:
				# Extract the user's display name from the JSON response
				user_data = response.json()
				user.current_display_name = user_data.get('display_name',
				                                          'Unknown User')  # Default value in case the field is missing
			else:
				user.current_display_name = 'Unknown User'

			user.save()  # Save tokens to the user model

		return redirect("library")
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
def make_wrapped(request, time_range='medium_term', limit=5):
	user = User.objects.get(username=request.session.get('username'))
	endpoint = 'https://api.spotify.com/v1/me'

	if not user.spotify_access_token:
		return JsonResponse({'error': 'User is not authenticated with Spotify.'}, status=401)

	headers = {'Authorization': f'Bearer {user.spotify_access_token}'}
	response = requests.get(endpoint, headers=headers)
	display_name = response.json()['display_name']

	if response.status_code == 401:
		access_token = refresh_spotify_token(user)
		if not access_token:
			return JsonResponse({'error': 'Failed to refresh access token.'}, status=400)
		user.spotify_access_token = access_token
		user.save()

	top_tracks = requests.get(f'{endpoint}/top/tracks?limit={limit}&time_range={time_range}', headers=headers)
	top_artists = requests.get(f'{endpoint}/top/artists?limit={limit}&time_range={time_range}', headers=headers)
	genre_req = requests.get(f'{endpoint}/top/artists?limit=20&time_range={time_range}', headers=headers)

	if top_tracks.status_code != 200 or top_artists.status_code != 200 or genre_req.status_code != 200:
		return JsonResponse({'error': 'Failed to retrieve data from Spotify'}, status=400)

	top_track_data = []
	for track in top_tracks.json()['items']:
		top_track_data.append({
			'track_name': track['name'],
			'track_id': track['id'],
			'album_name': track['album']['name'],
			'album_id': track['album']['name'],
			'artist_name': track['artists'][0]['name'],
			'artist_id': track['artists'][0]['id'],
			'popularity': track['popularity'],
			'cover_image': track['album']['images'][0]['url'],
			'preview': track['preview_url'],
		})

	top_artist_data = []
	for artist in top_artists.json()['items']:
		top_artist_data.append({
			'artist_name': artist['name'],
			'artist_id': artist['id'],
			'popularity': artist['popularity'],
			'artist_image': artist['images'][0]['url'],
		})

	top_genres = {}
	for artist in genre_req.json()['items']:
		for genre in artist['genres']:
			top_genres[genre] = top_genres.get(genre, 0) + 1

	data = {
		'time_range': time_range,
		'limit': limit,
		'top_tracks': top_track_data,
		'top_artists': top_artist_data,
		'top_genres': sorted(top_genres, key=top_genres.get),
	}
	# data['llama_description'] = llama_description(data)

	wrap = Wraps.objects.create(username=user.username, term=time_range, spotify_display_name=display_name,
	                            wrap_json=json.dumps(data))
	wrap.save()

	return get_wrapped(request, wrap.creation_date.isoformat())


@csrf_exempt
@login_required
def get_wrapped(request, dt):
	try:
		wrap = Wraps.objects.get(username=request.session.get('username'), creation_date=datetime.fromisoformat(dt))
	except Wraps.DoesNotExist:
		return JsonResponse({'error': 'Wrapped does not exist'}, status=404)

	return JsonResponse({'data': json.loads(wrap.wrap_json), 'dt': dt})


@csrf_exempt
@login_required
def get_game_tracks(request):
	user = User.objects.get(username=request.session.get('username'))
	endpoint = 'https://api.spotify.com/v1/me'

	if not user.spotify_access_token:
		return JsonResponse({'error': 'User is not authenticated with Spotify.'}, status=401)

	headers = {'Authorization': f'Bearer {user.spotify_access_token}'}
	response = requests.get(endpoint, headers={'Authorization': f'Bearer {user.spotify_access_token}'})

	if response.status_code == 401:
		access_token = refresh_spotify_token(user)
		if not access_token:
			return JsonResponse({'error': 'Failed to refresh access token.'}, status=400)
		user.spotify_access_token = access_token
		user.save()

	top_tracks = requests.get(f'{endpoint}/top/tracks?limit=50&time_range=long_term', headers=headers)
	tracks = []
	for track in top_tracks.json()['items']:
		tracks.append(track['name'])

	return render(request, 'Spotify_Wrapper/wrapper.html', {'tracks': tracks})


@csrf_exempt
@login_required
def llama_description(data):
	msg = "Based on the following list of top tracks, artists, and genres from a user's Spotify Wrapped, craft a fun, engaging, slightly sassy description of the personality, behavior, and style of someone who listens to this kind of music. Be playful and witty, but avoid being mean or overly critical. Tie the music preferences to relatable behaviors and quirks."
	client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=settings.SPOTIFY_REDIRECT_URI)
	completion = client.chat.completions.create(model="meta/llama-3.1-405b-instruct",
	                                            messages=[{"role": "user", "content": f"{msg}\n\n{data}"}],
	                                            temperature=0.2, top_p=0.7, max_tokens=1024, stream=True)
	info = ''
	info += (chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
	return JsonResponse({'info': info})
