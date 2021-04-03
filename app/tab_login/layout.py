import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H3('App 1'),
    dcc.Location(id='login-url', refresh=True),
    html.Div(id='login-page-contents'),
    dcc.Link('Go Home', href='/')
])