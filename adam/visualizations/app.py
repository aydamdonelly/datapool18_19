import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Import your modules
import modules.top_scorers as top_scorers
import modules.player_radar_charts as player_radar_charts
import modules.transfers_analysis as transfers_analysis
import modules.club_transfer_details as club_transfer_details
import modules.home_away_performance as home_away_performance

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Football Analysis Dashboard"

# Define the layout of the app
app.layout = dbc.Container([
    html.H1("Football Analysis Dashboard", className="text-center text-light my-4"),

    dbc.Tabs([
        dbc.Tab(label="Top Scorers", tab_id="top-scorers-tab"),
        dbc.Tab(label="Player Radar Charts", tab_id="player-radar-charts-tab"),
        dbc.Tab(label="Transfers Analysis", tab_id="transfers-analysis-tab"),
        dbc.Tab(label="Club Transfer Details", tab_id="club-transfer-details-tab"),
        dbc.Tab(label="Home & Away Performance", tab_id="home-away-performance-tab"),
    ], id="tabs", active_tab="top-scorers-tab"),

    html.Div(id="tab-content")
], fluid=True)

# Callback to render tab content
@app.callback(
    dash.dependencies.Output("tab-content", "children"),
    [dash.dependencies.Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "top-scorers-tab":
        return top_scorers.layout()
    elif active_tab == "player-radar-charts-tab":
        return player_radar_charts.layout()
    elif active_tab == "transfers-analysis-tab":
        return transfers_analysis.layout()
    elif active_tab == "club-transfer-details-tab":
        return club_transfer_details.layout()
    elif active_tab == "home-away-performance-tab":
        return home_away_performance.layout()

# Register callbacks for each module
top_scorers.register_callbacks(app)
player_radar_charts.register_callbacks(app)
transfers_analysis.register_callbacks(app)
club_transfer_details.register_callbacks(app)
home_away_performance.register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
