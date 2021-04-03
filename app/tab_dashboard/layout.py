from helpers_spotify import get_top_artists, get_top_tracks, get_track_audio_features, cluster_audio_features
import itertools
import collections
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import StandardScaler
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from config import RANGE, PLOTLY_TEMPLATE


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
