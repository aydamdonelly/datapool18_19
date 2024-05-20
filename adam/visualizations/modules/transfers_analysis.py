import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc

# Load the data
transfers_df = pd.read_csv('../data/filtered_arrivals_with_additional_data.csv')

# Define colors for positions
colors = {'DF': 'green', 'MF': 'blue', 'FW': 'red'}

# Categorize players by age groups
def categorize_age(age):
    if age < 25:
        return 'Under 25'
    elif 25 <= age <= 30:
        return '25-30'
    else:
        return 'Over 30'

transfers_df['Age Group'] = transfers_df['Age'].apply(categorize_age)

# Add trendlines for each position to the plot
def add_trendline(fig, df, position, color):
    df_position = df[df['Position'] == position]
    if len(df_position) > 1:
        z = np.polyfit(df_position['Fee'], df_position['Total Score'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df_position['Fee'],
            y=p(df_position['Fee']),
            mode='lines',
            name=f'Trendline {position}',
            line=dict(color=color, width=3),
            showlegend=True
        ))

# Add a trendline for the average age to the plot
def add_age_line(fig, df):
    df_sorted = df.sort_values('Fee')
    z = np.polyfit(df_sorted['Fee'], df_sorted['Age'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df_sorted['Fee'],
        y=p(df_sorted['Fee']),
        mode='lines',
        name='Average Age',
        line=dict(color='#FFCC00', width=3),  # Darker yellow for average age line
        yaxis='y2',
        showlegend=True
    ))

# Define the layout of the app
def layout():
    return html.Div([
        html.H1("Analysis of Player Transfer Fees and Total Scores", style={'font-size': '32px', 'text-align': 'center', 'margin-bottom': '20px'}),
        dcc.Dropdown(
            id='club-dropdown',
            options=[{'label': club, 'value': club} for club in transfers_df['Club'].unique()] + [{'label': 'All', 'value': 'All'}],
            value='All',
            multi=False,
            placeholder='Select a club',
            style={'margin-bottom': '20px'}
        ),
        dcc.Graph(id='scatter-plot')
    ])

# Register the callbacks for interactivity
def register_callbacks(app):
    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('club-dropdown', 'value')]
    )
    def update_scatter_plot(selected_club):
        filtered_df = transfers_df

        if selected_club != 'All':
            filtered_df = filtered_df[filtered_df['Club'] == selected_club]

        scatter_fig = px.scatter(
            filtered_df,
            x='Fee',
            y='Total Score',
            color='Position',
            color_discrete_map=colors,
            hover_data={'Player': True, 'Age': True, 'Fee': True, 'Total Score': True, 'Club': True, 'Position': True},
            labels={'Fee': 'Transfer Fee (€m)', 'Total Score': 'Total Score'},
            template='plotly'
        )

        scatter_fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=2, color='DarkSlateGrey')))
        scatter_fig.update_layout(
            height=670,  # Adjusted height to fit viewport
            xaxis=dict(
                title='Transfer Fee (€m)',
                title_font=dict(size=35, family='Arial, sans-serif', weight='bold'),
                tickfont=dict(size=26, family='Arial, sans-serif', weight='bold'),
                showline=True,
                linewidth=3,
                linecolor='gray'
            ),
            yaxis=dict(
                title='Total Score',
                title_font=dict(size=35, family='Arial, sans-serif', weight='bold'),
                tickfont=dict(size=26, family='Arial, sans-serif', weight='bold'),
                showline=True,
                linewidth=3,
                linecolor='gray'
            ),
            legend_title_text='Position',
            font=dict(color='black', family='Arial, sans-serif'),
            legend=dict(font=dict(size=16, family='Arial, sans-serif'), itemclick=False, itemdoubleclick=False),
            yaxis2=dict(
                title='Average Age',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[18, 35],
                titlefont=dict(size=18, family='Arial, sans-serif', weight='bold')
            ),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        for position, color in colors.items():
            add_trendline(scatter_fig, filtered_df, position, color)

        add_age_line(scatter_fig, filtered_df) 

        return scatter_fig

# Initialize Dash app and register callbacks
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout()
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
