import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc

# Load the data
transfers_df = pd.read_csv('../filtered_arrivals_with_additional_data.csv')

# Define colors for positions
colors = {'DF': 'green', 'MF': 'blue', 'FW': 'red'}

def categorize_age(age):
    if age < 25:
        return 'Under 25'
    elif 25 <= age <= 30:
        return '25-30'
    else:
        return 'Over 30'

transfers_df['Age Group'] = transfers_df['Age'].apply(categorize_age)

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

def add_age_line(fig, df):
    df_sorted = df.sort_values('Fee')
    z = np.polyfit(df_sorted['Fee'], df_sorted['Age'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df_sorted['Fee'],
        y=p(df_sorted['Fee']),
        mode='lines',
        name='Average Age',
        line=dict(color='yellow', width=3),
        yaxis='y2',
        showlegend=True
    ))

def layout():
    return html.Div([
        html.H1("Player Transfers Analysis", style={'color': 'orange'}),
        dcc.Dropdown(
            id='club-dropdown',
            options=[{'label': club, 'value': club} for club in transfers_df['Club'].unique()] + [{'label': 'All', 'value': 'All'}],
            value='All',
            multi=False,
            placeholder='Select a club',
            style={'backgroundColor': 'black', 'color': 'orange'}
        ),
        dcc.Dropdown(
            id='position-dropdown',
            options=[{'label': pos, 'value': pos} for pos in transfers_df['Position'].unique() if pd.notna(pos)] + [{'label': 'All', 'value': 'All'}],
            value='All',
            multi=False,
            placeholder='Select a position',
            style={'backgroundColor': 'black', 'color': 'orange'}
        ),
        dcc.Graph(id='scatter-plot')
    ], style={'backgroundColor': 'black'})

def register_callbacks(app):
    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('club-dropdown', 'value'),
         Input('position-dropdown', 'value')]
    )
    def update_scatter_plot(selected_club, selected_position):
        filtered_df = transfers_df

        if selected_club != 'All':
            filtered_df = filtered_df[filtered_df['Club'] == selected_club]
        
        if selected_position != 'All':
            filtered_df = filtered_df[filtered_df['Position'] == selected_position]

        scatter_fig = px.scatter(
            filtered_df,
            x='Fee',
            y='Total Score',
            color='Position',
            color_discrete_map=colors,
            hover_data={'Player': True, 'Age': True, 'Fee': True, 'Total Score': True, 'Club': True, 'Position': True},
            title="Scatter Plot of Fee vs. Total Score",
            labels={'Fee': 'Transfer Fee (€m)', 'Total Score': 'Total Score'},
            template='plotly_dark'
        )

        scatter_fig.update_traces(marker=dict(size=14, opacity=0.8))
        scatter_fig.update_layout(
            height=1600,
            xaxis_title='Transfer Fee (€m)',
            yaxis_title='Total Score',
            title={
                'text': "Scatter Plot of Fee vs. Total Score",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend_title_text='Position',
            font=dict(color='orange'),
            yaxis2=dict(
                title='Average Age',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[18, 35]
            )
        )

        for position, color in colors.items():
            add_trendline(scatter_fig, filtered_df, position, color)

        add_age_line(scatter_fig, filtered_df)

        return scatter_fig
