from openai import OpenAI
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
@login_required
def llama_request(request, other):
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="API_KEY_CALL"
    )
    completion = client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user",
                   "content": f"What kind of cuisine is served at {other}? Make sure your response takes up only 1 token."}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )
    info = ''
    for chunk in completion:
        if chunk.choices[0].delta.content:
            info += chunk.choices[0].delta.content
    return JsonResponse({'info': info})
