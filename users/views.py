import os
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Create your views here.
@login_required
def user_logout(request):
    logout(request)
    return redirect("home")
#*DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
def create_google_token(request, user):
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.events']
    )
    flow.redirect_uri = 'https://tutor-flow.com/users/google_calendar_redirect'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
    )

    # Save the state in the user's session
    request.session['oauth_state'] = state

    return authorization_url

def register(request):
    if request.method != 'POST':
        form = UserForm()
    else:
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            authorization_url = create_google_token(request, user)
            return redirect(authorization_url)

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def google_calendar_redirect(request):
    state = request.GET.get('state')

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        state=state
    )
    flow.redirect_uri = 'https://tutor-flow.com/users/google_calendar_redirect'

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save the credentials to the user's profile
    profile = request.user.profile
    profile.token = credentials.token
    profile.refresh_token = credentials.refresh_token
    profile.token_uri = credentials.token_uri
    profile.client_id = credentials.client_id
    profile.client_secret = credentials.client_secret
    profile.scopes = ','.join(credentials.scopes)
    profile.save()

    return redirect('calendar')