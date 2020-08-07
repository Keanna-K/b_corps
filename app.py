# authors: Keanna Knebel
# date: 2020-08-06

###############################################################################
# IMPORT PACKAGES                                                             #
###############################################################################

# Basics
import pandas as pd
import geopandas as gpd
import numpy as np
import random
import json
import re
from textwrap import dedent

# Plotly
import plotly.graph_objects as go
import plotly.express as px

# Dash
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

###############################################################################
# APP SET-UP                                                                  #
###############################################################################

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

###############################################################################
# READ-IN DATASETS                                                            #
###############################################################################

df = pd.read_csv("data/ont_bcorps.csv")

###############################################################################
# LAYOUT                                                                      #
###############################################################################

app.layout = html.Div([
    
    # Main app header
    html.Div([
        # Setting the main title of the Dashboard
        html.H1(
            "Ontario B Corporations"
        )
    ])
])

###############################################################################
# UPDATES + CALLBACKS                                                         #
###############################################################################

app.run_server(debug=True)
