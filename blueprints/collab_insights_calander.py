from flask import Blueprint, redirect, url_for, session, request, jsonify
from flask_login import login_required, current_user
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import datetime

calendar_bp = Blueprint('calendar_bp', __name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = 'client_secret.json'  # Update this path if needed

# Helper: Get credentials from session

def get_credentials():
    creds_data = session.get('google_creds')
    if creds_data:
        return Credentials.from_authorized_user_info(creds_data, SCOPES)
    return None

# OAuth2 login route
@calendar_bp.route('/google_calendar/login')
def google_calendar_login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar_bp.google_calendar_callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

# OAuth2 callback route
@calendar_bp.route('/google_calendar/callback')
def google_calendar_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar_bp.google_calendar_callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session['google_creds'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    return redirect(url_for('collab_bp.collab_insights_calendar', user_id=current_user.id))

# Fetch events for the logged-in user
@calendar_bp.route('/google_calendar/events')
@login_required
def google_calendar_events():
    creds = get_credentials()
    if not creds:
        return redirect(url_for('calendar_bp.google_calendar_login'))
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=20, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return jsonify(events)

# Create a new event
@calendar_bp.route('/google_calendar/create_event', methods=['POST'])
@login_required
def google_calendar_create_event():
    creds = get_credentials()
    if not creds:
        return redirect(url_for('calendar_bp.google_calendar_login'))
    data = request.json
    event = {
        'summary': data['summary'],
        'start': {'dateTime': data['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': data['end'], 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in data.get('attendees', [])],
    }
    service = build('calendar', 'v3', credentials=creds)
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify(created_event)
