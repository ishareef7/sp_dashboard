import os
import enum

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DIR_APP_DATA = os.path.join(ROOT_DIR, 'app_data')
DIR_APP_LOGS = os.path.join(ROOT_DIR, 'app_logs')
DIR_CONFIG = os.path.join(ROOT_DIR, 'config')

PATH_TO_DOTENV = os.path.join(DIR_CONFIG, '.env')
DIR_CACHE = os.path.join(DIR_APP_DATA, 'cache', '.cache')

SCOPE_LIST = ["user-read-recently-played", "user-top-read", "user-read-playback-position", "playlist-modify-public",
              "playlist-modify-private", "playlist-read-private", "playlist-read-collaborative",
              "user-library-modify", "user-library-read"
              ]

SCOPE_STRING = ' '.join(SCOPE_LIST)


class RANGE(enum.Enum):
    SHORT_TERM = 'short_term'
    MEDIUM_TERM = 'medium_term'
    LONG_TERM = 'long_term'


PLOTLY_TEMPLATE = 'ggplot2'
