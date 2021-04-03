import spotipy
import pandas as pd
from config import RANGE
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


def authenticate(access_token):
    sp = spotipy.Spotify(access_token)
    return sp


def get_top_artists(access_token, time_range=RANGE.MEDIUM_TERM.value, n=10):
    sp = authenticate(access_token)
    results = sp.current_user_top_artists(time_range=time_range, limit=n)
    top_artists = pd.DataFrame(data=results['items'])
    return top_artists


def get_top_tracks(access_token, time_range=RANGE.MEDIUM_TERM.value, n=10):
    sp = authenticate(access_token)
    results = sp.current_user_top_tracks(time_range=time_range, limit=n)
    top_tracks = pd.DataFrame(data=results['items'])
    return top_tracks


def get_track_audio_features(access_token, track_df: pd.DataFrame):
    sp = authenticate(access_token)
    results = sp.audio_features(track_df['id'].to_list())
    result_df = pd.DataFrame(data=results)
    use_cols = result_df.columns.difference(track_df.columns).append(pd.Index(['id']))
    audio_features_df = pd.merge(left=track_df, right=result_df[use_cols], on='id', how='left')
    return audio_features_df


def cluster_audio_features(audio_features_df, kmax=5):
    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness',
                    'loudness', 'speechiness', 'tempo', 'valence']
    features = audio_features_df[feature_cols]
    features = PCA(n_components=2).fit_transform(features)
    silhouette_scores = []
    n_clusters = list(range(2, kmax + 1))
    for k in n_clusters:
        model = KMeans(n_clusters=k).fit(features)
        cluster_labels = model.labels_
        model_score = silhouette_score(features, cluster_labels, metric='euclidean')
        silhouette_scores.append(model_score)

    best_k = n_clusters[silhouette_scores.index(max(silhouette_scores))]
    labels = KMeans(n_clusters=best_k).fit_predict(features)
    features = pd.DataFrame(data=features)
    features['cluster'] = labels
    return features, labels
