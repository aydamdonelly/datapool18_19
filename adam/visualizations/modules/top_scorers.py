import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('../GOALS_ONLY_SORTED_UPDATED.csv')

# Create a cumulative sum of goals for each player by match day
df['Cumulative Goals'] = df.groupby('Player').cumcount() + 1

# Aggregate goals by player and match day
agg_df = df.groupby(['MatchDay', 'Player', 'Squad']).size().reset_index(name='Goals')
agg_df['Cumulative Goals'] = agg_df.groupby(['Player', 'Squad'])['Goals'].cumsum()

# Get the top 10 players by total goals scored
total_goals = df.groupby(['Player', 'Squad'])['Cumulative Goals'].max().reset_index()
top_10_players = total_goals.nlargest(10, 'Cumulative Goals')['Player'].tolist()

# Filter data to include only the top 10 players
agg_df = agg_df[agg_df['Player'].isin(top_10_players)]

# Create a mapping from squads to colors
squad_colors = {
    'Liverpool': '#c8102e',
    'Leicester City': '#003090',
    'Manchester Utd': '#da291c',
    'Bournemouth': '#d71920',
    'Wolves': '#d1d1d1',
    'Tottenham Hotspur': '#d1d1d1',
    'Everton': '#003399',
    'Crystal Palace': '#1b458f',
    'Watford': '#fbec5d',
    'Manchester City': '#6cabdd',
    'Newcastle Utd': '#241f20',
    'Chelsea': '#034694',
    'Arsenal': '#ef0107'
}

def layout():
    return html.Div([
        dcc.Graph(id='top-scorers-graph', style={'position': 'relative', 'height': '950px'}),  # Adjusted height
        dcc.Slider(
            id='matchday-slider',
            min=agg_df['MatchDay'].min(),
            max=agg_df['MatchDay'].max(),
            value=agg_df['MatchDay'].min(),
            marks={str(day): str(day) for day in agg_df['MatchDay'].unique()},
            step=None
        ),
        html.Div([
            html.Button('Start Animation', id='start-button', n_clicks=0, style={'margin-right': '10px', 'font-size': '16px', 'padding': '10px'}),
            html.Button('Pause Animation', id='pause-button', n_clicks=0, style={'margin-right': '10px', 'font-size': '16px', 'padding': '10px'}),
            html.Button('Restart Animation', id='restart-button', n_clicks=0, style={'font-size': '16px', 'padding': '10px'}),
        ]),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # 1000 milliseconds = 1 second
            n_intervals=0,
            disabled=True
        ),
    ], style={'backgroundColor': 'white', 'color': 'black'})

def update_figure(selected_day):
    filtered_df = agg_df[agg_df['MatchDay'] <= selected_day]
    
    cumulative_goals = filtered_df.groupby(['Player', 'Squad'])['Cumulative Goals'].max().reset_index()
    cumulative_goals = cumulative_goals.set_index('Player').reindex(top_10_players).reset_index()
    cumulative_goals['Cumulative Goals'].fillna(0, inplace=True)

    cumulative_goals['Player'] = pd.Categorical(cumulative_goals['Player'], categories=top_10_players, ordered=True)
    cumulative_goals = cumulative_goals.sort_values('Player')
    cumulative_goals['Color'] = cumulative_goals['Squad'].map(squad_colors)

    fig = go.Figure(go.Bar(
        x=cumulative_goals['Cumulative Goals'],
        y=cumulative_goals['Player'],
        orientation='h',
        text=[f"{player}: {goals} Goals ({squad})" for player, goals, squad in zip(cumulative_goals['Player'], cumulative_goals['Cumulative Goals'], cumulative_goals['Squad'])],
        marker=dict(color=cumulative_goals['Color']),
        textposition='inside',
        textfont=dict(size=22, color="white", family='Arial, sans-serif', weight='bold')  # Increased font size and made it bold
    ))
    
    fig.update_layout(
        title=f'Premier League top scorers on matchday {selected_day}',
        title_x=0.5,
        title_font=dict(size=24, family='Arial, sans-serif', color='black', weight='bold'),
        yaxis=dict(categoryorder='total ascending', tickwidth=2, showticklabels=False, zeroline=True, showline=True, linecolor='black', linewidth=2),
        margin=dict(l=200, r=20, t=80, b=40),
        xaxis=dict(range=[0, 25], title='Number of goals', tickwidth=2, zeroline=True, showline=True, linecolor='black', linewidth=2),
        transition={'duration': 1000, 'easing': 'cubic-in-out'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )

    fig.add_annotation(
        text=f"MATCHDAY {selected_day}",
        xref="paper", yref="paper",
        x=0.95, y=0.05,
        font=dict(size=30, color="Grey"),
        showarrow=False,
        opacity=0.8
    )

    return fig

def register_callbacks(app):
    @app.callback(
        [Output('top-scorers-graph', 'figure'),
         Output('interval-component', 'disabled'),
         Output('interval-component', 'n_intervals'),
         Output('matchday-slider', 'value')],
        [Input('start-button', 'n_clicks'),
         Input('pause-button', 'n_clicks'),
         Input('restart-button', 'n_clicks'),
         Input('interval-component', 'n_intervals'),
         Input('matchday-slider', 'value')],
        [State('interval-component', 'disabled'),
         State('interval-component', 'n_intervals')]
    )
    def update_output(start_n_clicks, pause_n_clicks, restart_n_clicks, n_intervals, slider_value, interval_disabled, current_intervals):
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update, interval_disabled, dash.no_update, slider_value

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'start-button':
            return dash.no_update, False, slider_value - agg_df['MatchDay'].min(), slider_value

        if trigger_id == 'pause-button':
            return dash.no_update, True, current_intervals, slider_value

        if trigger_id == 'restart-button':
            return dash.no_update, False, 0, agg_df['MatchDay'].min()

        if trigger_id == 'matchday-slider':
            selected_day = slider_value
            fig = update_figure(selected_day)
            return fig, True, n_intervals, selected_day

        selected_day = agg_df['MatchDay'].min() + n_intervals
        if selected_day > agg_df['MatchDay'].max():
            return dash.no_update, True, n_intervals, slider_value

        fig = update_figure(selected_day)
        return fig, True if trigger_id == 'matchday-slider' else interval_disabled, n_intervals, selected_day
