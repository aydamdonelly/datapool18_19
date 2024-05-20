import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Pfad zur CSV-Datei
file_path = '../op_players_list_with_percentiles.csv'

# Laden der CSV-Datei
df = pd.read_csv(file_path)

# Listen der relevanten Statistiken für jede Position
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

# Initialisieren der Dash-App
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Funktion zur Erstellung der Dropdown-Optionen
def create_dropdown_options(position):
    return [
        {'label': f"{player} ({club}, {age}, {nation})", 'value': player}
        for player, club, age, nation in zip(df[df['Position'] == position]['Player'], df[df['Position'] == position]['Club'], df[df['Position'] == position]['Age'], df[df['Position'] == position]['Nation'])
    ]

# Funktion zur Erstellung der erweiterten Tabelle
def create_horizontal_table(players_stats, stats):
    data = {'Statistic per 90': ['Player', 'Club', 'Age', 'Minutes played'] + stats}
    for player_stats in players_stats:
        data[player_stats['Player']] = [
            player_stats['Player'], player_stats['Club'], player_stats['Age'], player_stats['Minutes played']
        ] + [round(player_stats[stat], 2) for stat in stats]
    return pd.DataFrame(data).to_dict('records')

# Funktion zur Erstellung eines leeren Radar-Charts
def create_empty_radar_chart():
    fig = go.Figure()
    fig.update_layout(
        template='plotly_dark',
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

# Erstellen der Layout-Komponenten
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("Select Attacking Players", style={'color': 'orange'}),
            dcc.Dropdown(
                id='attacker-dropdown',
                options=create_dropdown_options('FW'),
                multi=True,
                placeholder="Select attacking players",
                style={'backgroundColor': 'black', 'color': 'orange'}
            ),
            dcc.Graph(id='attacker-radar-chart', figure=create_empty_radar_chart()),
            dash_table.DataTable(
                id='attacker-table', 
                style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                style_header={'backgroundColor': 'black', 'color': 'orange'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Select Midfield Players", style={'color': 'orange'}),
            dcc.Dropdown(
                id='midfielder-dropdown',
                options=create_dropdown_options('MF'),
                multi=True,
                placeholder="Select midfield players",
                style={'backgroundColor': 'black', 'color': 'orange'}
            ),
            dcc.Graph(id='midfielder-radar-chart', figure=create_empty_radar_chart()),
            dash_table.DataTable(
                id='midfielder-table', 
                style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                style_header={'backgroundColor': 'black', 'color': 'orange'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Select Defensive Players", style={'color': 'orange'}),
            dcc.Dropdown(
                id='defender-dropdown',
                options=create_dropdown_options('DF'),
                multi=True,
                placeholder="Select defensive players",
                style={'backgroundColor': 'black', 'color': 'orange'}
            ),
            dcc.Graph(id='defender-radar-chart', figure=create_empty_radar_chart()),
            dash_table.DataTable(
                id='defender-table', 
                style_table={'overflowX': 'auto', 'whiteSpace': 'normal'}, 
                style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                style_header={'backgroundColor': 'black', 'color': 'orange'}
            )
        ], width=12)
    ])
])

# Callback zum Aktualisieren des Angreifer-Diagramms und der Tabelle basierend auf der Auswahl
@app.callback(
    [Output('attacker-radar-chart', 'figure'),
     Output('attacker-table', 'data'),
     Output('attacker-table', 'columns')],
    [Input('attacker-dropdown', 'value')]
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
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],  # Den Kreis schließen
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],  # Den Kreis schließen
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = df[df['Player'] == player][attacker_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,  # Sichtbarkeit der radialen Achse ausschalten
                range=[0, 100]  # Bereich der radialen Achse auf 0 bis 100 setzen
            ),
            angularaxis=dict(
                visible=True  # Sichtbarkeit der angularen Achse aktivieren
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, attacker_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

# Callback zum Aktualisieren des Mittelfeld-Diagramms und der Tabelle basierend auf der Auswahl
@app.callback(
    [Output('midfielder-radar-chart', 'figure'),
     Output('midfielder-table', 'data'),
     Output('midfielder-table', 'columns')],
    [Input('midfielder-dropdown', 'value')]
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
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],  # Den Kreis schließen
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],  # Den Kreis schließen
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = df[df['Player'] == player][midfielder_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,  # Sichtbarkeit der radialen Achse ausschalten
                range=[0, 100]  # Bereich der radialen Achse auf 0 bis 100 setzen
            ),
            angularaxis=dict(
                visible=True  # Sichtbarkeit der angularen Achse aktivieren
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, midfielder_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

# Callback zum Aktualisieren des Verteidiger-Diagramms und der Tabelle basierend auf der Auswahl
@app.callback(
    [Output('defender-radar-chart', 'figure'),
     Output('defender-table', 'data'),
     Output('defender-table', 'columns')],
    [Input('defender-dropdown', 'value')]
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
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],  # Den Kreis schließen
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],  # Den Kreis schließen
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = df[df['Player'] == player][defender_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,  # Sichtbarkeit der radialen Achse ausschalten
                range=[0, 100]  # Bereich der radialen Achse auf 0 bis 100 setzen
            ),
            angularaxis=dict(
                visible=True  # Sichtbarkeit der angularen Achse aktivieren
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, defender_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

# Starten der Dash-App
if __name__ == '__main__':
    app.run_server(debug=True)
