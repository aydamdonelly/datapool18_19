import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Load the dataset
df = pd.read_csv("adrian/data/all_shots_CLandPL.csv")

# Ensure xG and PSxG columns are numeric
df['xG'] = pd.to_numeric(df['xG'], errors='coerce')
df['PSxG'] = pd.to_numeric(df['PSxG'], errors='coerce')

# Filter for Liverpool players
df_liverpool = df[df['Squad'] == 'Liverpool']

# Calculate total goals for each player
goal_counts = df_liverpool[df_liverpool['Outcome'] == 'Goal'].groupby('Player').size().reset_index(name='Goals')

# Filter players with at least 5 goals
players_with_5_goals = goal_counts[goal_counts['Goals'] >= 5]['Player'].tolist()

# Filter for rows where the player is one of the selected players
df_filtered = df_liverpool[df_liverpool['Player'].isin(players_with_5_goals)]

# Define the app
app = dash.Dash(__name__)

# Define player options
players = df_filtered['Player'].unique()

# Define shot plot function
def plot_player_shots(player_name):
    # Filter for rows where the player is the selected player
    df_player = df_filtered[df_filtered['Player'] == player_name]

    # Filter for shots on target (Outcome is either 'Goal' or 'Saved')
    df_player_on_target = df_player[df_player['Outcome'].isin(['Goal', 'Saved'])]

    # Define the outcome order
    outcome_order = {'Goal': 1, 'Saved': 2}

    # Add a column for outcome sorting
    df_player_on_target['Outcome_Order'] = df_player_on_target['Outcome'].map(outcome_order)

    # Sort by outcome order first, then by PSxG descending
    df_player_sorted = df_player_on_target.sort_values(by=['PSxG'], ascending=[True])

    # Reset the index to get shot IDs for the sorted DataFrame
    df_player_sorted.reset_index(drop=True, inplace=True)
    df_player_sorted['Shot_ID'] = df_player_sorted.index + 1  # Shot IDs starting from 1

    # Initialize the figure
    fig = make_subplots()

    # Add scatter traces for each shot
    for index, row in df_player_sorted.iterrows():
        xg_value = row['xG']
        psxg_value = row['PSxG']
        shot_id = row['Shot_ID']
        outcome = row['Outcome']

        # Determine the color and legend group for the outcome marker
        if outcome == 'Goal':
            outcome_color = 'green'
            legend_group = 'Goal'
        elif outcome == 'Saved':
            outcome_color = 'red'
            legend_group = 'Saved'
        else:
            outcome_color = 'blue'
            legend_group = 'xG before Shot'

        # Calculate the difference between xG and PSxG for hover text
        difference = psxg_value - xg_value if not pd.isna(psxg_value) else None
        # Round the difference to two decimal places
        difference = round(difference, 2) if difference is not None else None

        # Define the custom hover template
        hover_template = f"<b>xG:</b> {xg_value}<br><b>PSxG:</b> {psxg_value}<br><b>Difference:</b> {difference}"

        # Add the initial xG marker
        fig.add_trace(
            go.Scatter(
                x=[xg_value],
                y=[shot_id],
                mode='markers',
                marker=dict(size=10, color='blue', opacity=0.6),  # Set color to blue
                name=None,  # Do not show legend for initial xG markers
                legendgroup=legend_group,  # Group for the legend
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
                    name=None,  # Do not show legend for PSxG markers
                    legendgroup=legend_group,  # Group for the legend
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=hover_template
                )
            )

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

            # Add line shape to connect xG to PSxG
            fig.add_shape(
                type="line",
                x0=xg_value, y0=shot_id,
                x1=psxg_value, y1=shot_id,
                line=dict(color="gray", width=2),
                opacity=0.7,
                xref="x", yref="y"
            )

    # Add invisible traces for legend explanation
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

    # Update layout
    fig.update_layout(
        title=f"Expected Goals xG and Post-Shot-xG for {player_name}'s On-Target Shots",
        xaxis_title='xG/PSxG',
        yaxis_title='Shot No.',
        template='plotly_white',
        height=800,
        showlegend=True
    )

    return fig


# Define app layout
app.layout = html.Div([
    html.H1("Expected Goals xG and Post-Shot-xG with at Least 5 Goals"),
    html.Label("Select a player:"),
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in players],
        value=players[0]  # Default to the first player
    ),
    dcc.Graph(id='shot-graph')
])

# Define callback to update the shot graph based on player selection
@app.callback(
    Output('shot-graph', 'figure'),
    [Input('player-dropdown', 'value')]
)
def update_shot_graph(selected_player):
    return plot_player_shots(selected_player)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)











































