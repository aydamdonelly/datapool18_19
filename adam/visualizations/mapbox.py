import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Load the data from a CSV file
df = pd.read_csv('../transfer_data.csv')

# Convert 'Fee' to numeric, handling non-numeric data as NaN and then replacing NaN with 0
df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)

# Filter to include only Liverpool FC and the 2018/2019 season
df_lfc = df[(df['Club'] == 'Liverpool') & (df['Season'] == '2018/2019')]

# Example data with geographical coordinates (latitude and longitude)
# This data should ideally come from a reliable source or be part of the dataset
club_locations = {
    'Liverpool': {'lat': 53.4308, 'lon': -2.9608},
    'Southampton': {'lat': 50.9078, 'lon': -1.4039},
    'AS Roma': {'lat': 41.8947, 'lon': 12.4722},
    'RB Leipzig': {'lat': 51.3455, 'lon': 12.3838},
    # Add other clubs as needed
}

# Adding geographical coordinates to the dataframe
df_lfc['lat'] = df_lfc['Club'].map(lambda x: club_locations.get(x, {}).get('lat'))
df_lfc['lon'] = df_lfc['Club'].map(lambda x: club_locations.get(x, {}).get('lon'))

# Initialize the Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Liverpool FC 2018/2019 Transfers"  # Title for the browser tab

# Layout of the Dash application
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Liverpool FC 2018/2019 Transfer Activities", className="text-center my-4")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Select Transfer Type:', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='transfer-type-dropdown',
                options=[
                    {'label': 'Arrivals', 'value': 'Arrival'},
                    {'label': 'Departures', 'value': 'Departure'}
                ],
                value='Arrival',
                clearable=False,
                style={'width': '50%', 'margin': 'auto'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='mapbox-plot')
        ], width=12)
    ])
], fluid=True, style={'padding': '20px'})

# Callback to update the map plot
@app.callback(
    Output('mapbox-plot', 'figure'),
    [Input('transfer-type-dropdown', 'value')]
)
def update_mapbox_plot(selected_transfer_type):
    # Filter data based on selected transfer type
    filtered_df = df_lfc[df_lfc['Transfer'] == selected_transfer_type]

    # Filter out rows with missing coordinates
    filtered_df = filtered_df.dropna(subset=['lat', 'lon'])

    # Create a Mapbox scatter plot
    fig = px.scatter_mapbox(
        filtered_df,
        lat='lat',
        lon='lon',
        hover_name='Player',
        hover_data={'Fee': ':.2f', 'lat': False, 'lon': False},
        color='Transfer',
        size='Fee',
        size_max=15,
        zoom=1,
        mapbox_style='open-street-map',
        title='Liverpool FC 2018/2019 Transfer Activities'
    )

    fig.update_layout(
        margin={'r': 0, 't': 50, 'l': 0, 'b': 0},
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=53.4308, lon=-2.9608),  # Centering map on Liverpool
            zoom=3
        )
    )

    return fig

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
