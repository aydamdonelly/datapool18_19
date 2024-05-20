import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px

# Load the data
df = pd.read_csv('../GOALS_ONLY_SORTED.csv')

# Create a cumulative sum of goals for each player by match day
df['Cumulative Goals'] = df.groupby('Player').cumcount() + 1

# Aggregate goals by player and match day
agg_df = df.groupby(['MatchDay', 'Player', 'Squad']).size().reset_index(name='Goals')
agg_df['Cumulative Goals'] = agg_df.groupby(['Player', 'Squad'])['Goals'].cumsum()

# Get the top 10 players by total goals scored
total_goals = agg_df.groupby('Player')['Cumulative Goals'].max().reset_index()
top_10_players = total_goals.nlargest(10, 'Cumulative Goals')['Player'].tolist()

# Filter data to include only the top 10 players
agg_df = agg_df[agg_df['Player'].isin(top_10_players)]

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Graph(id='top-scorers-graph', style={'height': '1000px', 'position': 'relative'}),
    html.Div([
        html.Button('Start Animation', id='start-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('Pause Animation', id='pause-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('Restart Animation', id='restart-button', n_clicks=0),
    ], style={'position': 'relative', 'zIndex': '1'}),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1000 milliseconds = 1 second
        n_intervals=0,
        disabled=True
    ),
])

@app.callback(
    [Output('top-scorers-graph', 'figure'),
     Output('interval-component', 'disabled'),
     Output('interval-component', 'n_intervals')],
    [Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks'),
     Input('restart-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('interval-component', 'disabled'),
     State('interval-component', 'n_intervals')]
)
def update_output(start_n_clicks, pause_n_clicks, restart_n_clicks, n_intervals, interval_disabled, current_intervals):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, interval_disabled, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'start-button':
        return dash.no_update, False, current_intervals

    if trigger_id == 'pause-button':
        return dash.no_update, True, current_intervals

    if trigger_id == 'restart-button':
        return dash.no_update, False, 0

    selected_day = agg_df['MatchDay'].min() + n_intervals
    if selected_day > agg_df['MatchDay'].max():
        return dash.no_update, True, n_intervals

    # Filter the data up to the selected match day
    filtered_df = agg_df[agg_df['MatchDay'] <= selected_day]
    
    # Ensure all top 10 players are always included even if they have 0 goals at the beginning
    cumulative_goals = filtered_df.groupby(['Player', 'Squad'])['Cumulative Goals'].max().reset_index()
    cumulative_goals = cumulative_goals.set_index('Player').reindex(top_10_players).reset_index()
    cumulative_goals['Cumulative Goals'].fillna(0, inplace=True)

    # Maintain the order of the top 10 players
    cumulative_goals['Player'] = pd.Categorical(cumulative_goals['Player'], categories=top_10_players, ordered=True)
    cumulative_goals = cumulative_goals.sort_values('Player')

    # Create a horizontal bar chart with player names and squads inside the bars
    fig = px.bar(cumulative_goals, x='Cumulative Goals', y='Player', orientation='h', 
                 title=f'Top 10 Scorers up to MatchDay {selected_day}',
                 labels={'Cumulative Goals': 'Cumulative Goals', 'Player': 'Player'},
                 text='Cumulative Goals',
                 color='Player',
                 hover_data={'Squad': True})

    # Add "MATCHDAY {selected_day}" text in the background at the bottom right
    fig.add_annotation(
        text=f"MATCHDAY {selected_day}",
        xref="paper", yref="paper",
        x=0.95, y=0.05,
        font=dict(size=30, color="Grey"),
        showarrow=False,
        opacity=0.8
    )
    
    # Update the layout for better visualization
    fig.update_layout(yaxis={'categoryorder': 'total ascending'},
                      height=1000,
                      margin=dict(l=200, r=20, t=40, b=40),
                      xaxis={'range': [0, 25]},  # Fixed range for X-axis
                      yaxis_title=None,
                      transition={'duration': 1000, 'easing': 'cubic-in-out'},
                      yaxis_visible=False)

    fig.update_traces(
        texttemplate='%{y}: %{text} (%{customdata[0]})',  # Show player and squad
        textposition='inside',
        marker=dict(line=dict(width=1)),
        textfont=dict(size=24, color="black")  # Increase font size and change color
    )

    return fig, False, n_intervals

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
