import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc

# Load the data
df = pd.read_csv('../data/entire_players_list_with_percentiles.csv')

# Define relevant statistics for each position
attacker_stats = [
    'Goals', 'Assists', 'Expected Goals', 'Expected Assisted Goals', 'Progressive Passes Received',
    'Shot creating actions', 'Crosses into penalty area', 'Successful take ons',
    'Goals per shot on target', 'Shots on target %', 'Aerial duels won %', 'Carries into final 1/3'
]
midfielder_stats = [
    'Passes completed', 'Progressive passes', 'Passes into final third', 'Shot creating actions',
    'Interceptions', 'Balls blocked', 'Expected Assisted Goals', 'Carries into final 1/3',
    'Goals', 'Touches', 'Long passes completed %', 'Clearances'
]
defender_stats = [
    'Tackles won %', 'Clearances', 'Interceptions', 'Progressive moved ball distance', 'Progressive passes',
    'Aerial duels won %', 'Balls blocked', 'Recoveries', 'Passes attempted', 'Errors', 'Fouls committed', 'Progressive pass distance', 'Yellow cards'
]

# Creating dropdown options for each player based on their position
def create_dropdown_options(position):
    return [
        {'label': f"{player} ({club}, {age}, {nation})", 'value': player}
        for player, club, age, nation in zip(df[df['Position'] == position]['Player'], df[df['Position'] == position]['Club'], df[df['Position'] == position]['Age'], df[df['Position'] == position]['Nation'])
    ]

# Creating an empty radar chart as a placeholder
def create_empty_radar_chart():
    fig = go.Figure()
    fig.update_layout(
        template='plotly',
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 100]
            ),
            angularaxis=dict(
                visible=True
            )
        ),
        showlegend=False
    )
    return fig

# Creating a horizontal table for displaying player stats
def create_horizontal_table(players_stats, stats):
    data = {'Statistic per 90': ['Player', 'Club', 'Age', 'Minutes played'] + stats}
    for player_stats in players_stats:
        data[player_stats['Player']] = [
            player_stats['Player'], player_stats['Club'], player_stats['Age'], player_stats['Minutes played']
        ] + [round(player_stats[stat], 2) for stat in stats]
    return pd.DataFrame(data).to_dict('records')

def layout():
    return dbc.Container([
        html.H1("Top 5 League Players Radar Chart", style={'textAlign': 'center', 'fontWeight': 'bold', 'margin-top': '20px'}),
        html.P("Data sources: FBRef", style={'text-align': 'center', 'font-size': '12px', 'color': 'gray', 'margin-top': '0'}),
        html.P(
            "The statistics the players are being compared in differ based on the position you are looking at. Each radar chart shows the percentile rankings of the selected players when compared to players from the top 5 leagues in their position.",
            style={'textAlign': 'center', 'fontSize': '18px', 'margin-bottom': '30px'}
        ),
        dbc.Row([
            dbc.Col([
                html.H3("Select Attacking Players", style={'font-size': '24px', 'font-weight': 'bold', 'margin-bottom': '15px'}),
                dcc.Dropdown(
                    id='attacker-dropdown',
                    options=create_dropdown_options('FW'),
                    multi=True,
                    placeholder="Select attacking players",
                    style={'margin-bottom': '15px'}
                ),
                dcc.Graph(id='attacker-radar-chart', figure=create_empty_radar_chart()),
                html.H5("", style={'textAlign': 'center', 'margin-top': '10px'}),
                html.P(
                    "",
                    style={'textAlign': 'center', 'font-size': '14px', 'margin-bottom': '20px'}
                ),
                dash_table.DataTable(
                    id='attacker-table', 
                    style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                    style_cell={'textAlign': 'left', 'fontSize': '14px', 'font-family': 'Arial'},
                    style_header={'fontWeight': 'bold'}
                )
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Select Midfield Players", style={'font-size': '24px', 'font-weight': 'bold', 'margin-bottom': '15px'}),
                dcc.Dropdown(
                    id='midfielder-dropdown',
                    options=create_dropdown_options('MF'),
                    multi=True,
                    placeholder="Select midfield players",
                    style={'margin-bottom': '15px'}
                ),
                dcc.Graph(id='midfielder-radar-chart', figure=create_empty_radar_chart()),
                html.H5("", style={'textAlign': 'center', 'margin-top': '10px'}),
                html.P(
                    "",
                    style={'textAlign': 'center', 'font-size': '14px', 'margin-bottom': '20px'}
                ),
                dash_table.DataTable(
                    id='midfielder-table', 
                    style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                    style_cell={'textAlign': 'left', 'fontSize': '14px', 'font-family': 'Arial'},
                    style_header={'fontWeight': 'bold'}
                )
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Select Defensive Players", style={'font-size': '24px', 'font-weight': 'bold', 'margin-bottom': '15px'}),
                dcc.Dropdown(
                    id='defender-dropdown',
                    options=create_dropdown_options('DF'),
                    multi=True,
                    placeholder="Select defensive players",
                    style={'margin-bottom': '15px'}
                ),
                dcc.Graph(id='defender-radar-chart', figure=create_empty_radar_chart()),
                html.H5("", style={'textAlign': 'center', 'margin-top': '10px'}),
                html.P(
                    "",
                    style={'textAlign': 'center', 'font-size': '14px', 'margin-bottom': '20px'}
                ),
                dash_table.DataTable(
                    id='defender-table', 
                    style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                    style_cell={'textAlign': 'left', 'fontSize': '14px', 'font-family': 'Arial'},
                    style_header={'fontWeight': 'bold'}
                )
            ], width=12)
        ])
    ])

def register_callbacks(app):
    @app.callback(
        Output('attacker-radar-chart', 'figure'),
        Output('attacker-table', 'data'),
        Output('attacker-table', 'columns'),
        Input('attacker-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_attacker_chart(selected_players):
        if not selected_players:
            return create_empty_radar_chart(), [], []

        fig = go.Figure()
        players_stats = []

        for player in selected_players:
            player_data = df[df['Player'] == player].iloc[0]
            stats = [category + '_percentile' for category in attacker_stats]
            fig.add_trace(go.Scatterpolar(
                r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
                theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
                fill='toself',
                name=player,
                hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
            ))
            player_stats = df[df['Player'] == player][attacker_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
            players_stats.append(player_stats)

        fig.update_layout(
            template='plotly',
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 100]
                ),
                angularaxis=dict(
                    visible=True
                )
            ),
            showlegend=True,
            annotations=[
                go.layout.Annotation(
                    text="Radar chart shows the percentile rankings of the selected players in various statistics.",
                    x=0.5,
                    y=1.1,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="darkslategray", family="Arial, sans-serif", weight='bold'),
                    align="center",
                    borderpad=10,
                    yshift=40  # Add some space below the annotation
                )
            ]
        )

        table_data = create_horizontal_table(players_stats, attacker_stats)
        columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
        
        return fig, table_data, columns

    @app.callback(
        Output('midfielder-radar-chart', 'figure'),
        Output('midfielder-table', 'data'),
        Output('midfielder-table', 'columns'),
        Input('midfielder-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_midfielder_chart(selected_players):
        if not selected_players:
            return create_empty_radar_chart(), [], []

        fig = go.Figure()
        players_stats = []

        for player in selected_players:
            player_data = df[df['Player'] == player].iloc[0]
            stats = [category + '_percentile' for category in midfielder_stats]
            fig.add_trace(go.Scatterpolar(
                r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
                theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
                fill='toself',
                name=player,
                hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
            ))
            player_stats = df[df['Player'] == player][midfielder_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
            players_stats.append(player_stats)

        fig.update_layout(
            template='plotly',
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 100]
                ),
                angularaxis=dict(
                    visible=True
                )
            ),
            showlegend=True,
            annotations=[
                go.layout.Annotation(
                    text="Radar chart shows the percentile rankings of the selected players in various statistics.",
                    x=0.5,
                    y=1.1,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="darkslategray", family="Arial, sans-serif", weight='bold'),
                    align="center",
                    borderpad=10,
                    yshift=40  # Add some space below the annotation
                )
            ]
        )

        table_data = create_horizontal_table(players_stats, midfielder_stats)
        columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
        
        return fig, table_data, columns

    @app.callback(
        Output('defender-radar-chart', 'figure'),
        Output('defender-table', 'data'),
        Output('defender-table', 'columns'),
        Input('defender-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_defender_chart(selected_players):
        if not selected_players:
            return create_empty_radar_chart(), [], []

        fig = go.Figure()
        players_stats = []

        for player in selected_players:
            player_data = df[df['Player'] == player].iloc[0]
            stats = [category + '_percentile' for category in defender_stats]
            fig.add_trace(go.Scatterpolar(
                r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
                theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
                fill='toself',
                name=player,
                hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
            ))
            player_stats = df[df['Player'] == player][defender_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
            players_stats.append(player_stats)

        fig.update_layout(
            template='plotly',
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 100]
                ),
                angularaxis=dict(
                    visible=True
                )
            ),
            showlegend=True,
            annotations=[
                go.layout.Annotation(
                    text="Radar chart shows the percentile rankings of the selected players in various statistics.",
                    x=0.5,
                    y=1.1,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="darkslategray", family="Arial, sans-serif", weight='bold'),
                    align="center",
                    borderpad=10,
                    yshift=40  # Add some space below the annotation
                )
            ]
        )

        table_data = create_horizontal_table(players_stats, defender_stats)
        columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
        
        return fig, table_data, columns

# Initialize the Dash app and register callbacks
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout()
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
