import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Einlesen der CSV-Datei
transfers_df = pd.read_csv('../filtered_arrivals_with_additional_data.csv')

# Altersgruppen hinzufügen
def categorize_age(age):
    if age < 25:
        return 'Under 25'
    elif 25 <= age <= 30:
        return '25-30'
    else:
        return 'Over 30'

transfers_df['Age Group'] = transfers_df['Age'].apply(categorize_age)

# Trendlinien-Funktion für jede Position
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
            line=dict(color=color, dash='dash')
        ))

# Farben für die Trendlinien
colors = {
    'DF': 'blue',
    'MF': 'green',
    'FW': 'red'
}

# Dash-Anwendung initialisieren
app = dash.Dash(__name__)

# Layout der Dash-Anwendung
app.layout = html.Div([
    html.H1("Player Transfers Analysis"),
    dcc.Dropdown(
        id='club-dropdown',
        options=[{'label': club, 'value': club} for club in transfers_df['Club'].unique()] + [{'label': 'All', 'value': 'All'}],
        value='All',
        multi=False,
        placeholder='Select a club'
    ),
    dcc.Dropdown(
        id='position-dropdown',
        options=[{'label': pos, 'value': pos} for pos in transfers_df['Position'].unique()] + [{'label': 'All', 'value': 'All'}],
        value='All',
        multi=False,
        placeholder='Select a position'
    ),
    dcc.Graph(id='scatter-plot')
])

# Callback-Funktion für die Interaktivität
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
        hover_data=['Player', 'Age', 'Fee', 'Total Score', 'Club', 'Position'],
        title="Scatter Plot of Fee vs. Total Score",
        labels={'Fee': 'Transfer Fee (€m)', 'Total Score': 'Total Score'},
        template='plotly_dark'
    )

    scatter_fig.update_layout(
        xaxis_title='Transfer Fee (€m)',
        yaxis_title='Total Score',
        title={
            'text': "Scatter Plot of Fee vs. Total Score",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend_title_text='Position'
    )

    for position, color in colors.items():
        add_trendline(scatter_fig, filtered_df, position, color)

    return scatter_fig

# Anwendung ausführen
if __name__ == '__main__':
    app.run_server(debug=True)
