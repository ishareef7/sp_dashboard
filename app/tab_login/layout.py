import dash_core_components as dcc
import dash_html_components as html

login_page = html.Div([
    dcc.Link('Login', href='/app/tab_login'),
])