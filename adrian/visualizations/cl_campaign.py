import pandas as pd
import plotly.graph_objects as go
# import plotly.express as px

df_results = pd.read_csv("adrian/data/cl_results.csv")
df_players = pd.read_csv("adrian/data/cl_season_standard_stats.csv")

# calculate total goals scored, conceded, wins, draws, and losses (cols 1 and 2)
total_goals_scored = df_results['GF'].sum()
total_goals_conceded = df_results['GA'].sum()
total_wins = (df_results['Result'] == 'W').sum()
total_draws = (df_results['Result'] == 'D').sum()
total_losses = (df_results['Result'] == 'L').sum()

# calculate total goals and assists by players (cols 3 and 4)
player_goals = df_players.groupby('Player')['Gls'].sum().sort_values(ascending=False)
player_assists = df_players.groupby('Player')['Ast'].sum().sort_values(ascending=False)

# filter for players with at least one goal or assist
players_with_goals = set(player_goals[player_goals > 0].index)
players_with_assists = set(player_assists[player_assists > 0].index)
players_with_goals_or_assists = players_with_goals.union(players_with_assists)


# define function to generate random unqiue colors 
# every player should have a distinct color
def generate_color_gradient(index, max_index):
    # define RGB components for red and blue
    red = (255, 0, 0)
    blue = (0, 0, 255)

    # calculate proportions of red and blue based on the player's index
    red_proportion = 1 - ((index / max_index) ** 0.5)  
    blue_proportion = (index / max_index) ** 0.5 

    # calculate RGB values for the color based on the gradient
    r = int(red[0] * red_proportion + blue[0] * blue_proportion)
    g = int(red[1] * red_proportion + blue[1] * blue_proportion)
    b = int(red[2] * red_proportion + blue[2] * blue_proportion)

    # format rgb into hex code
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

    return hex_color

# create mapping of players to colors based on the color gradient
player_colors = {player: generate_color_gradient(index, len(players_with_goals_or_assists) - 1) 
                 for index, player in enumerate(players_with_goals_or_assists)}

# calculate total number of "bricks" (one rectangle) for each column
total_bricks_goals = total_goals_scored + total_goals_conceded
total_bricks_results = total_wins + total_draws + total_losses
total_bricks_players_goals = player_goals.sum()
total_bricks_players_assists = player_assists.sum()

# calculate brick height for each column (all columns should have same size in the end)
brick_height_goals = 100 / total_bricks_goals
brick_height_results = 100 / total_bricks_results
brick_height_players_goals = 100 / total_bricks_players_goals
brick_height_players_assists = 100 / total_bricks_players_assists

# Create "waffle"/ bar fusion plot 
fig = go.Figure()

# column widths and starting positions
column_width = 0.5
column_positions = [0, 1.0, 2.0, 3.0]

# trace for goals scored (col 1)
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
    
# trace for goals conceded (col 1)
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
    
# trace for wins (col 2)
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
    
# trace for draws (col 2)
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
    
# trace for losses (col 2)
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
    
# scatter trace for goals by players (col 3)
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
    
# scatter trace for assists by players (col 4)
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
    yaxis=dict(
        visible=False,  # make the y-axis invisible (just looks cooler)
    ),
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',  # make the plot background transparent
)


fig.show()






































































