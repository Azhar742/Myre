# Collab Insights (Gmail & Google Meet integration) page

from models.user_model import User
from models.account_model import Account
from decorators import validate_user_access

from utils.utils import serialize_account
from controllers.priority_condition_controller import get_accounts_by_user_priority_conditions_service

from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from flask_login import login_required, current_user
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import datetime

collab_bp = Blueprint('collab_bp', __name__)

@collab_bp.route('/dashboard/<int:user_id>/collab_insights', methods=['GET'])
@validate_user_access
def collab_insights(user_id):
    user = User.query.get(user_id)
    return render_template('html/collab_insights.html', user_id=user_id, user_email=user.user_email)


@collab_bp.route('/dashboard/<int:user_id>/collab_insights/email', methods=['GET'])
def collab_insights_email(user_id):
    user = User.query.get(user_id)
    return render_template('html/collab_insights_email.html', user_id=user_id, user_email=user.user_email)

@collab_bp.route('/dashboard/<int:user_id>/collab_insights/calendar', methods=['GET'])
def collab_insights_calendar(user_id):
    print(user_id)
    user = User.query.get(user_id)
    print(user)
    if not user:
        return "User not found", 404
    return render_template('html/collab_insights_calendar.html', user_id=user_id, user_email=user.user_email)

@collab_bp.route('/dashboard/<int:user_id>/collab_insights/moms', methods=['GET'])
def collab_insights_moms(user_id):
    user = User.query.get(user_id)
    return render_template('html/collab_insights_moms.html', user_id=user_id, user_email=user.user_email)

@collab_bp.route('/dashboard/<int:user_id>/collab_insights/calls', methods=['GET'])
def collab_insights_calls(user_id):
    user = User.query.get(user_id)
    return render_template('html/collab_insights_calls.html', user_id=user_id, user_email=user.user_email)

# Google Calendar integration for collab insights
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = 'client_secret.json'

def get_credentials():
    creds_data = session.get('google_creds')
    if creds_data:
        return Credentials.from_authorized_user_info(creds_data, SCOPES)
    return None

@collab_bp.route('/google_calendar/login')
def google_calendar_login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('collab_bp.google_calendar_callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@collab_bp.route('/google_calendar/callback')
def google_calendar_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('collab_bp.google_calendar_callback', _external=True)
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

@collab_bp.route('/google_calendar/events')
@login_required
def google_calendar_events():
    creds = get_credentials()
    if not creds:
        return redirect(url_for('collab_bp.google_calendar_login'))
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=20, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return jsonify(events)

@collab_bp.route('/google_calendar/create_event', methods=['POST'])
@login_required
def google_calendar_create_event():
    creds = get_credentials()
    if not creds:
        return redirect(url_for('collab_bp.google_calendar_login'))
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