import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

df = pd.read_csv("adrian/data/all_shots_CLandPL.csv")

# just to ensure xG and PSxG columns are numeric
df['xG'] = pd.to_numeric(df['xG'], errors='coerce')
df['PSxG'] = pd.to_numeric(df['PSxG'], errors='coerce')

df_liverpool = df[df['Squad'] == 'Liverpool']

# calculate total goals for each player
# we will only take Liverpool players that have scored 5+ goals across the season
goal_counts = df_liverpool[df_liverpool['Outcome'] == 'Goal'].groupby('Player').size().reset_index(name='Goals')
players_with_5_goals = goal_counts[goal_counts['Goals'] >= 5]['Player'].tolist()

# filter for rows where the player is one of the selected players
df_filtered = df_liverpool[df_liverpool['Player'].isin(players_with_5_goals)]

app = dash.Dash(__name__)

players = df_filtered['Player'].unique()

# define shot plot function
def plot_player_shots(player_name):
    df_player = df_filtered[df_filtered['Player'] == player_name]

    # filter for shots on target (outcome is either 'Goal' or 'Saved')
    df_player_on_target = df_player[df_player['Outcome'].isin(['Goal', 'Saved'])]

    # sort ascendingly by PSxG (just more visually pleasing)
    df_player_sorted = df_player_on_target.sort_values(by=['PSxG'], ascending=[True])

    # reset the index to get shot IDs for the sorted df (one shot per "line"/"row")
    df_player_sorted.reset_index(drop=True, inplace=True)
    df_player_sorted['Shot_ID'] = df_player_sorted.index + 1 
    
    fig = make_subplots()

    # add scatter traces for each shot
    for index, row in df_player_sorted.iterrows():
        xg_value = row['xG']
        psxg_value = row['PSxG']
        shot_id = row['Shot_ID']
        outcome = row['Outcome']

        # define the color and legend group for the outcome marker
        if outcome == 'Goal':
            outcome_color = 'green'
            legend_group = 'Goal'
        elif outcome == 'Saved':
            outcome_color = 'red'
            legend_group = 'Saved'
        else:
            outcome_color = 'blue'
            legend_group = 'xG before Shot'

        # calculate difference between xG and PSxG for hover text
        difference = psxg_value - xg_value if not pd.isna(psxg_value) else None
        # round difference (before, it was too many decimal places)
        difference = round(difference, 2) if difference is not None else None

        # custom hover template
        hover_template = f"<b>xG:</b> {xg_value}<br><b>PSxG:</b> {psxg_value}<br><b>Difference:</b> {difference}"

        # add initial xG marker
        fig.add_trace(
            go.Scatter(
                x=[xg_value],
                y=[shot_id],
                mode='markers',
                marker=dict(size=10, color='blue', opacity=0.6),  
                name=None,  
                legendgroup=legend_group, 
                showlegend=False,
                hoverinfo='text',
                hovertext=hover_template
            )
        )
        # Add the PSxG marker and the line connecting xG to PSxG if PSxG is present
        if not pd.isna(psxg_value):
            fig.add_trace(
                go.Scatter(
                    x=[psxg_value],
                    y=[shot_id],
                    mode='markers',
                    marker=dict(size=10, color=outcome_color, opacity=0.6),
                    name=None,  
                    legendgroup=legend_group, 
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=hover_template
                )
            )
            # displaying lines as arrows between datapoints (just to look cool)
            fig.add_annotation(
                x=psxg_value,
                y=shot_id,
                text='',
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=1,
                arrowcolor="gray",
                ax=xg_value,
                ay=shot_id,
                axref='x',
                ayref='y',
                xref='x',
                yref='y',
                showarrow=True
            )

            # add line shape to connect xG to PSxG
            fig.add_shape(
                type="line",
                x0=xg_value, y0=shot_id,
                x1=psxg_value, y1=shot_id,
                line=dict(color="gray", width=2),
                opacity=0.7,
                xref="x", yref="y"
            )

    # add invisible traces for legend explanation
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='green'),
            name='Goal',
            showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Saved',
            showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='blue'),
            name='xG before Shot',
            showlegend=True
        )
    )

    fig.update_layout(
        title=f"Expected Goals xG and Post-Shot-xG for {player_name}'s On-Target Shots",
        xaxis_title='xG/PSxG',
        yaxis_title='Shot No.',
        template='plotly_white',
        height=800,
        showlegend=True
    )

    return fig

app.layout = html.Div([
    html.H1("Expected Goals xG and Post-Shot-xG: Liverpool players with at Least 5 Goals"),
    html.Label("Select a player:"),
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in players],
        value=players[0]  # Default to the first player
    ),
    dcc.Graph(id='shot-graph')
])

# callback to update the shot graph based on player selection
# before, there was a problem that the graph was not redrawn properly
@app.callback(
    Output('shot-graph', 'figure'),
    [Input('player-dropdown', 'value')]
)
def update_shot_graph(selected_player):
    return plot_player_shots(selected_player)

if __name__ == '__main__':
    app.run_server(debug=True)











































