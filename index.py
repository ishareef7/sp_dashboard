import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import spotipy
from dash.dependencies import Input, Output, State
from spotipy import SpotifyOAuth, CacheFileHandler
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SCOPE_STRING, DIR_CACHE, RANGE, \
    PLOTLY_TEMPLATE
from dash_app import dash_app
from helpers_spotify import get_top_artists, get_top_tracks, get_track_audio_features, cluster_audio_features
import itertools
import collections
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import StandardScaler
from app.tab_login.layout import login_page

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


def top_artists_viz(access_token, time_range: RANGE):
    top_artist_df = get_top_artists(access_token=access_token, time_range=time_range.value)
    list_items = []
    for i, artist_id in top_artist_df['id'].items():
        name = top_artist_df.loc[top_artist_df['id'] == artist_id, 'name'].squeeze()
        image_url = top_artist_df.loc[top_artist_df['id'] == artist_id, 'images'].squeeze()[0]['url']
        img_div = html.Img(src=image_url, style={'border-radius': '50%', 'width': '30px', 'float': 'left',
                                                 'margin-right': '5%', 'align': 'center'})
        heading = dbc.ListGroupItemHeading(f"{i + 1}. {name}")
        list_items.append(dbc.ListGroupItem(children=[img_div, heading]))

    top_artist_card = dbc.Card(children=[
        dbc.CardHeader(children=[html.H4("Top Artists")]),
        dbc.ListGroup(
            list_items,
            flush=True,
            style={'overflow': 'scroll', 'max-height': '400px'}
        ),
    ]
    )
    return top_artist_card


def top_genres_viz(access_token, time_range: RANGE):
    top_artist_df = get_top_artists(access_token=access_token, time_range=time_range.value)
    genres = list(itertools.chain.from_iterable(top_artist_df['genres'].to_list()))
    genre_counts = collections.Counter(genres)
    genre_df = pd.DataFrame.from_dict(genre_counts, orient='index').reset_index().rename(columns={'index': 'genre',
                                                                                                  0: 'count'})
    genre_df['genre'] = genre_df['genre'].str.title()
    figure = px.bar(genre_df, x='count', y='genre', template=PLOTLY_TEMPLATE, orientation='h',
                    labels={'count': 'Count', 'genre': 'Genre'})
    graph = dcc.Graph(id='genre-chart', figure=figure)
    graph_card = dbc.Card(
        children=[
            dbc.CardHeader(children=[html.H4("Genres of Top Artists")]),
            graph
        ]
    )
    return graph_card


def top_tracks_viz(access_token, time_range: RANGE):
    top_tracks_df = get_top_tracks(access_token=access_token, time_range=time_range.value)
    list_items = []
    for i, track_id in top_tracks_df['id'].items():
        name = top_tracks_df.loc[top_tracks_df['id'] == track_id, 'name'].squeeze()
        image_url = top_tracks_df.loc[top_tracks_df['id'] == track_id, 'album'].squeeze()['images'][0]['url']
        img_div = html.Img(src=image_url, style={'border-radius': '50%', 'width': '30px', 'float': 'left',
                                                 'margin-right': '5%', 'align': 'center'})
        heading = dbc.ListGroupItemHeading(f"{i + 1}. {name}")
        list_items.append(dbc.ListGroupItem(children=[img_div, heading]))

    top_tracks_card = dbc.Card(children=[
        dbc.CardHeader(children=[html.H4("Top Tracks")]),
        dbc.ListGroup(
            list_items,
            flush=True,
            style={'overflow': 'scroll', 'max-height': '400px'}
        )
    ]
    )
    return top_tracks_card


def audio_features_viz(access_token, time_range: RANGE):
    top_tracks_df = get_top_tracks(access_token=access_token, time_range=time_range.value)
    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness',
                    'loudness', 'speechiness', 'tempo', 'valence']

    audio_features_df = get_track_audio_features(access_token=access_token,
                                                 track_df=top_tracks_df)[feature_cols + ['id', 'name']]
    scaler = StandardScaler()
    audio_features_df[feature_cols] = scaler.fit_transform(audio_features_df[feature_cols])
    audio_features_df_melted = audio_features_df.melt(id_vars=['id', 'name'])
    figure = px.line_polar(data_frame=audio_features_df_melted,
                           r='value',
                           theta='variable',
                           color='name',
                           line_close=True,
                           template=PLOTLY_TEMPLATE,
                           labels=dict(zip(feature_cols, map(str.title, feature_cols)))
                           )
    figure.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.1,
        xanchor="right",
        x=1
    ))
    figure.update_traces(fill='toself')
    graph = dcc.Graph(id='audio-features-chart', figure=figure)
    graph_card = dbc.Card(
        children=[
            dbc.CardHeader(children=[html.H4("Top Track Audio Features")]),
            graph
        ]
    )
    return graph_card


def audio_features_clusters_viz(access_token, time_range: RANGE):
    top_tracks_df = get_top_tracks(access_token=access_token, time_range=time_range.value, n=50)
    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness',
                    'loudness', 'speechiness', 'tempo', 'valence']

    audio_features_df = get_track_audio_features(access_token=access_token,
                                                 track_df=top_tracks_df)[feature_cols + ['id', 'name']]

    features, labels = cluster_audio_features(audio_features_df)

    figure = px.scatter(features, x=0, y=1, color="cluster")

    graph = dcc.Graph(id='audio-features-cluster-chart', figure=figure)
    graph_card = dbc.Card(
        children=[
            dbc.CardHeader(children=[html.H4("Top Track Clusters")]),
            graph
        ]
    )
    return graph_card

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



def make_dashboard_page(user_data, time_range: RANGE = RANGE.MEDIUM_TERM):
    dashboard_page = [
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.CardDeck(
                        [
                            top_artists_viz(access_token=user_data['token'], time_range=time_range),
                            top_genres_viz(access_token=user_data['token'], time_range=time_range)
                        ]
                            )
                )
            ],
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.CardDeck(
                        [
                            top_tracks_viz(access_token=user_data['token'], time_range=time_range),
                            audio_features_viz(access_token=user_data['token'], time_range=time_range)
                        ]
                    )
                )
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    audio_features_clusters_viz(access_token=user_data['token'], time_range=RANGE.LONG_TERM)
                )
            ]
        )
    ]
    return dashboard_page


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
