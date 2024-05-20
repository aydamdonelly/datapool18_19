import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

# Load data
df_results = pd.read_csv("../../adrian/data/cl_results.csv")
df_players = pd.read_csv("../../adrian/data/cl_season_standard_stats.csv")

# Calculate metrics
total_goals_scored = df_results['GF'].sum()
total_goals_conceded = df_results['GA'].sum()
total_wins = (df_results['Result'] == 'W').sum()
total_draws = (df_results['Result'] == 'D').sum()
total_losses = (df_results['Result'] == 'L').sum()

player_goals = df_players.groupby('Player')['Gls'].sum().sort_values(ascending=False)
player_assists = df_players.groupby('Player')['Ast'].sum().sort_values(ascending=False)

players_with_goals = set(player_goals[player_goals > 0].index)
players_with_assists = set(player_assists[player_assists > 0].index)
players_with_goals_or_assists = players_with_goals.union(players_with_assists)

def generate_color_gradient(index, max_index):
    red = (255, 0, 0)
    blue = (0, 0, 255)
    red_proportion = 1 - ((index / max_index) ** 0.5)  
    blue_proportion = (index / max_index) ** 0.5 
    r = int(red[0] * red_proportion + blue[0] * blue_proportion)
    g = int(red[1] * red_proportion + blue[1] * blue_proportion)
    b = int(red[2] * red_proportion + blue[2] * blue_proportion)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

player_colors = {player: generate_color_gradient(index, len(players_with_goals_or_assists) - 1) 
                 for index, player in enumerate(players_with_goals_or_assists)}

total_bricks_goals = total_goals_scored + total_goals_conceded
total_bricks_results = total_wins + total_draws + total_losses
total_bricks_players_goals = player_goals.sum()
total_bricks_players_assists = player_assists.sum()

brick_height_goals = 100 / total_bricks_goals
brick_height_results = 100 / total_bricks_results
brick_height_players_goals = 100 / total_bricks_players_goals
brick_height_players_assists = 100 / total_bricks_players_assists

def create_figure():
    fig = go.Figure()
    column_width = 0.5
    column_positions = [0, 1.0, 2.0, 3.0]

    for i in range(total_goals_scored):
        fig.add_shape(
            type="rect",
            x0=column_positions[0],
            y0=i * brick_height_goals,
            x1=column_positions[0] + column_width,
            y1=(i + 1) * brick_height_goals,
            fillcolor="#1F77B4",
            line=dict(color="white"),
            opacity=0.7
        )
        fig.add_trace(go.Scatter(
            x=[column_positions[0] + column_width / 2],
            y=[i * brick_height_goals + brick_height_goals / 2],
            mode="markers",
            marker=dict(size=0.1, color="#1F77B4"),
            showlegend=False,
            hoverinfo="text",
            text=f"Goal {i + 1}: Scored"
        ))
    
    for i in range(total_goals_conceded):
        fig.add_shape(
            type="rect",
            x0=column_positions[0],
            y0=total_goals_scored * brick_height_goals + i * brick_height_goals,
            x1=column_positions[0] + column_width,
            y1=total_goals_scored * brick_height_goals + (i + 1) * brick_height_goals,
            fillcolor="#D62728",
            line=dict(color="white"),
            opacity=0.7
        )
        fig.add_trace(go.Scatter(
            x=[column_positions[0] + column_width / 2],
            y=[total_goals_scored * brick_height_goals + i * brick_height_goals + brick_height_goals / 2],
            mode="markers",
            marker=dict(size=0.1, color="#D62728"),
            showlegend=False,
            hoverinfo="text",
            text=f"Goal {i + 1}: Conceded"
        ))

    for i in range(total_wins):
        fig.add_shape(
            type="rect",
            x0=column_positions[1],
            y0=i * brick_height_results,
            x1=column_positions[1] + column_width,
            y1=(i + 1) * brick_height_results,
            fillcolor="#2CA02C",
            line=dict(color="white"),
            opacity=0.7
        )
        fig.add_trace(go.Scatter(
            x=[column_positions[1] + column_width / 2],
            y=[i * brick_height_results + brick_height_results / 2],
            mode="markers",
            marker=dict(size=0.1, color="#2CA02C"),
            showlegend=False,
            hoverinfo="text",
            text=f"Win {i + 1}"
        ))

    for i in range(total_draws):
        fig.add_shape(
            type="rect",
            x0=column_positions[1],
            y0=total_wins * brick_height_results + i * brick_height_results,
            x1=column_positions[1] + column_width,
            y1=total_wins * brick_height_results + (i + 1) * brick_height_results,
            fillcolor="#FF7F0E",
            line=dict(color="white"),
            opacity=0.7
        )
        fig.add_trace(go.Scatter(
            x=[column_positions[1] + column_width / 2],
            y=[total_wins * brick_height_results + i * brick_height_results + brick_height_results / 2],
            mode="markers",
            marker=dict(size=0.1, color="#FF7F0E"),
            showlegend=False,
            hoverinfo="text",
            text=f"Draw {i + 1}"
        ))

    for i in range(total_losses):
        fig.add_shape(
            type="rect",
            x0=column_positions[1],
            y0=total_wins * brick_height_results + total_draws * brick_height_results + i * brick_height_results,
            x1=column_positions[1] + column_width,
            y1=total_wins * brick_height_results + total_draws * brick_height_results + (i + 1) * brick_height_results,
            fillcolor="#D62728",
            line=dict(color="white"),
            opacity=0.7
        )
        fig.add_trace(go.Scatter(
            x=[column_positions[1] + column_width / 2],
            y=[total_wins * brick_height_results + total_draws * brick_height_results + i * brick_height_results + brick_height_results / 2],
            mode="markers",
            marker=dict(size=0.1, color="#D62728"),
            showlegend=False,
            hoverinfo="text",
            text=f"Loss {i + 1}"
        ))

    current_height_goals = 0
    for player, goals in player_goals.items():
        for i in range(goals):
            fig.add_shape(
                type="rect",
                x0=column_positions[2],
                y0=current_height_goals + i * brick_height_players_goals,
                x1=column_positions[2] + column_width,
                y1=current_height_goals + (i + 1) * brick_height_players_goals,
                fillcolor=player_colors[player],
                line=dict(color="white"),
                opacity=0.7
            )
            fig.add_trace(go.Scatter(
                x=[column_positions[2] + column_width / 2],
                y=[current_height_goals + i * brick_height_players_goals + brick_height_players_goals / 2],
                mode="markers",
                marker=dict(size=0.1, color=player_colors[player]),
                showlegend=False,
                hoverinfo="text",
                text=f"{player}: Goal {i + 1}"
            ))
        current_height_goals += goals * brick_height_players_goals

    current_height_assists = 0
    for player, assists in player_assists.items():
        for i in range(assists):
            fig.add_shape(
                type="rect",
                x0=column_positions[3],
                y0=current_height_assists + i * brick_height_players_assists,
                x1=column_positions[3] + column_width,
                y1=current_height_assists + (i + 1) * brick_height_players_assists,
                fillcolor=player_colors[player],
                line=dict(color="white"),
                opacity=0.7
            )
            fig.add_trace(go.Scatter(
                x=[column_positions[3] + column_width / 2],
                y=[current_height_assists + i * brick_height_players_assists + brick_height_players_assists / 2],
                mode="markers",
                marker=dict(size=0.1, color=player_colors[player]),
                showlegend=False,
                hoverinfo="text",
                text=f"{player}: Assist {i + 1}"
            ))
        current_height_assists += assists * brick_height_players_assists

    fig.update_layout(
        title="Liverpool's Champions League Triumph in Numbers - Goals, Match Results, Goalscorers and Assist Providers",
        xaxis=dict(
            tickmode='array',
            tickvals=[pos + column_width / 2 for pos in column_positions],
            ticktext=['Goals', 'Match Results', 'Goals per Player', 'Assists per Player']
        ),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def layout():
    return html.Div([
        dcc.Graph(figure=create_figure())
    ])

def register_callbacks(app):
    pass  # No callbacks needed for this visualization
