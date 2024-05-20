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

    # explanation text for xG metric
    fig.add_annotation(
        x=0.7,
        y=0.2,
        xref='paper',
        yref='paper',
        text="""Basically, Expected Goals (xG) is a metric to indicate how likely <br> 
                a shot is to result in a goal. It is being calculated from several features, <br> 
                such as the location of the shot, the body part that has been used for the shot, etc. <br> 
                Therefore, a comparison of xG and scored goals in one season can create insights on how <br>
                well a team took its chances, or also how "lucky" they were in shooting scenarios. <br>""",
        showarrow=False,
        font=dict(size=16, family='Arial, sans-serif', color='grey'),
        xanchor="center",
        yanchor="middle",
        bordercolor="black",
        bgcolor="white", 
    )
    
    fig.update_layout(
        title='xG-Over-/Underperformance at the End of the Season',
        title_font=dict(size=32, family='Arial, sans-serif', color='black', weight='bold'),
        xaxis_title='xG Difference',
        yaxis_title='Club',
        height = 800,
        yaxis=dict(tickmode='linear', 
                    title_font=dict(size=28, family='Arial, sans-serif', color='black', weight='bold'),
                    tickfont=dict(size=16, family='Arial, sans-serif', color='gray', weight='bold'), 
                   fixedrange=True,
                    showline=True,
                    linewidth=3,
                    linecolor='gray'),
        xaxis=dict(fixedrange=True,
                title_font=dict(size=28, family='Arial, sans-serif', color='black', weight='bold'),
                    tickfont=dict(size=16, family='Arial, sans-serif', color='gray', weight='bold'),
                    showline=True,
                    linewidth=3,
                    linecolor='gray'),
    )

    return fig

def layout():
    return html.Div([
        dcc.Graph(figure=create_figure()),
        html.P("Data source: FBref", style={'text-align': 'center', 'font-size': '12px', 'color': 'gray'})

    ])

def register_callbacks(app):
    pass  # No callbacks needed for this visualization
