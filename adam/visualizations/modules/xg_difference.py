import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

# Load data
df = pd.read_csv("../../adrian/data/pl_club_results.csv")

# Process data
df['Accumulated GF'] = 0
df['Accumulated xG'] = 0
club_info = {}

for index, row in df.iterrows():
    club = row['Club']
    gf = row['GF']
    xg = row['xG']
    
    if club not in club_info:
        club_info[club] = {'Accumulated GF': 0, 'Accumulated xG': 0}
    
    club_info[club]['Accumulated GF'] += gf
    club_info[club]['Accumulated xG'] += xg
    
    df.at[index, 'Accumulated GF'] = club_info[club]['Accumulated GF']
    df.at[index, 'Accumulated xG'] = club_info[club]['Accumulated xG']

end_of_season_df = df[df['Round'] == "Matchweek 38"]
end_of_season_df['xG_difference'] = end_of_season_df['Accumulated GF'] - end_of_season_df['Accumulated xG']
end_of_season_df = end_of_season_df.sort_values(by='xG_difference', ascending=True)

hover_text = [f"<b>{club}</b><br>"
              f"Goals: {int(goals)}<br>"
              f"xG: {xg:.1f}<br>"
              f"xG Difference: {xg_diff:.1f}"
              for club, goals, xg, xg_diff in zip(end_of_season_df['Club'],
                                                   end_of_season_df['Accumulated GF'],
                                                   end_of_season_df['Accumulated xG'],
                                                   end_of_season_df['xG_difference'])]

def create_figure():
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=end_of_season_df['Club'],
        x=end_of_season_df['xG_difference'],
        marker_color='indianred',
        orientation='h', 
        hoverinfo='text',
        hovertext=hover_text  
    ))

    fig.update_layout(
        title='xG-Over-/Underperformance at the End of the Season',
        xaxis_title='xG Difference',
        yaxis_title='Club',
        yaxis=dict(tickmode='linear', fixedrange=True), 
        xaxis=dict(fixedrange=True),
    )

    return fig

def layout():
    return html.Div([
        dcc.Graph(figure=create_figure())
    ])

def register_callbacks(app):
    pass  # No callbacks needed for this visualization
