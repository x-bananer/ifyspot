from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import os
from urllib.parse import urlencode
import httpx
import secrets
import base64
from app.crud.user import create_or_update
from app.database import SessionLocal

from app.config import SPOTIFY_CLIENT_ID
from app.config import SPOTIFY_CLIENT_SECRET
from app.config import SPOTIFY_REDIRECT_URI

router = APIRouter()

@router.get('/auth/login')
def login():
    scope = 'user-read-email  playlist-read-private'
    state = secrets.token_urlsafe(16)

    params = {
        'response_type': 'code',
        'client_id': SPOTIFY_CLIENT_ID,
        'scope': scope,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'state': state
    }

    url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
    return RedirectResponse(url)

@router.get('/auth/callback')
async def callback(request: Request):
    code = request.query_params.get('code')

    if not code:
        return {
            'error': {
                'status': 400,
                'message': 'No \'code\' parameter provided'
            }
        }

    auth_url = 'https://accounts.spotify.com/api/token'
    
    auth_params = {
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    auth_str = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {b64_auth_str}'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            auth_url,
            data=auth_params,
            headers=auth_headers
        )
    
    token_data = response.json()
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    if not access_token:
        return {
            'error': {
                'status': 400,
                'message': 'Failed to get access token'
            }
        }

    user_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            'https://api.spotify.com/v1/me',
            headers=user_headers
        )

    spotify_user_data = user_response.json()

    db = SessionLocal()
    db_user_data = {
        'spotify_id': spotify_user_data.get('id'),
        'display_name': spotify_user_data.get('display_name'),
        'email': spotify_user_data.get('email'),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    user = create_or_update(db, db_user_data)
    db.close()

    return {
        'id': user.id,
        'spotify_id': db_user_data['spotify_id'],
        'display_name': db_user_data['display_name'],
        'email': db_user_data['email'],
        'token': f'Bearer {access_token}',
    }
