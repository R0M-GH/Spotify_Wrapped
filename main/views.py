import base64
import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI


@login_required
def home(request):
	return render(request, 'index.html', {})


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
def search_artist(token, artist_name):
	url = "https://api.spotify.com/v1/search"
	headers = {"Authorization": "Bearer " + token}
	query = f"?q={artist_name}&type=artist&limit=1"
	query_url = url + query
	result = requests.get(query_url, headers=headers)
	print(result.content)
	return json.loads(result.content)


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
