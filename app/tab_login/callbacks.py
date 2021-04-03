import os
import spotipy
from dash.dependencies import Input, Output
from dash_app import dash_app
import dash_core_components as dcc

@dash_app.callback(Output('login-page-contents', 'children'),
                   Input('login-url', 'pathname'))
def auth():
    access_token = ""
    token_info = credentials_manager.get_cached_token()

    if token_info:
        print("Using Cached Token")
        access_token = token_info['access_token']
    else:
        url = credentials_manager.get_auth_response()
        code = credentials_manager.parse_response_code(url)
        if code != url:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = credentials_manager.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results

    else:
        print('here')
        return login_link()
