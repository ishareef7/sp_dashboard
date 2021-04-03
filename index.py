import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import spotipy
from dash.dependencies import Input, Output, State
from spotipy import SpotifyOAuth, CacheFileHandler
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SCOPE_STRING, DIR_CACHE, RANGE
from dash_app import dash_app
from app.tab_login.layout import login_page
from app.tab_dashboard.layout import make_dashboard_page

credentials_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                   scope=SCOPE_STRING,
                                   cache_handler=CacheFileHandler(cache_path=DIR_CACHE),
                                   show_dialog=True)


def get_auth_url():
    auth_url = credentials_manager.get_authorize_url()
    return auth_url


def login_link():
    auth_url = get_auth_url()
    link = dcc.Link('Login', href=auth_url)
    return link


def auth():
    access_token = ""
    token_info = credentials_manager.validate_token(credentials_manager.cache_handler.get_cached_token())
    if token_info:
        print("Using Cached Token")
        access_token = token_info['access_token']
    else:
        response = credentials_manager.get_auth_response()
        if response:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            access_token = credentials_manager.get_access_token(response, as_dict=False)

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results, access_token

    else:
        print('here')
        return login_link()


def make_banner(photo_url=None):
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Spotify Dashboard"),
                    html.H6("Listening History Analysis"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Img(id="profile-photo", src=photo_url, style={'border-radius': '50%'}),
                ],
            ),
        ],
    )


dash_app.layout = html.Div(
    id="big-app-container",
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='token-store', storage_type='session'),
        html.Div(id='hidden-redirect'),
        dbc.Row(children=[
            dbc.Col(make_banner())
        ]),
        dbc.Container(id="app-content")

    ],
)


@dash_app.callback([Output('app-content', 'children'),
                    Output('token-store', 'data'),
                    Output('hidden-redirect', 'children'),
                    Output('profile-photo', 'src')],
                   Input('url', 'pathname'),
                   State('token-store', 'data'))
def display_page(pathname, data):
    profile_photo = None
    redirect = dcc.Location(id='url', pathname='/', refresh=True)
    if pathname == '/':
        if data:
            if len(data['user_dict']['images']) > 0:
                profile_photo = data['user_dict']['images'][0]['url']
            return make_dashboard_page(user_data=data), data, None, profile_photo
        else:
            return login_page, None, None, profile_photo
    elif pathname == '/app/tab_login':
        results, access_token = auth()
        if isinstance(results, dict):
            data = data or {'token': access_token}
            data['user_dict'] = results
            return None, data, redirect, profile_photo
        else:
            return login_page, data, redirect, profile_photo
    else:
        return '404', None, None


if __name__ == '__main__':
    dash_app.run_server(debug=True)
