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

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Club Transfer Details"  # Title for the browser tab

# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Club Transfer Details", className="text-center my-4", style={'color': '#FFFFFF'})
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Select Season:', className="h5", style={'color': '#FFFFFF'}),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in df['Season'].unique()],
                value='2018/2019',
                multi=False,
                placeholder='Select a season',
                className="mb-4"
            )
        ], width=6, className="offset-md-3")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-plot', config={'displayModeBar': False})
        ], width=12)
    ])
], fluid=True, style={'backgroundColor': '#1f2c56', 'padding': '20px'})

# Callback to update the bar plot based on selected season
@app.callback(
    Output('bar-plot', 'figure'),
    [Input('season-dropdown', 'value')]
)
def update_bar_plot(selected_season):
    filtered_df = df[df['Season'] == selected_season]

    fig = px.bar(
        filtered_df,
        x='Club',
        y='Fee',
        color='Transfer',
        barmode='group',
        title=f'Club Transfer Details for {selected_season} Season',
        labels={'Fee': 'Fee (in Million €)'},
        hover_data=['Player', 'Position'],
        template='plotly_dark'
    )

    # Customize the hover information
    fig.update_traces(
        hovertemplate='<br>'.join([
            'Player: %{customdata[0]}',
            'Position: %{customdata[1]}',
            "Fee: %{y:,.2f}M €"
        ])
    )

    # Adjust layout options
    fig.update_layout(
        xaxis_title="Club",
        yaxis_title="Fee (in Million €)",
        plot_bgcolor='#1f2c56',
        paper_bgcolor='#1f2c56',
        font=dict(color='white'),
        title_font=dict(size=20, color='white'),
        legend_title_text='Transfer Type',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
