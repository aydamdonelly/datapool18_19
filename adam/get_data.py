from statsbombpy import sb

def fetch_liverpool_matches(season_name):
    # Lade alle Spiele für die Premier League Saison 2018/19
    matches = sb.matches(competition_id=2, season_id=season_name)

    # Filtere die Spiele, bei denen Liverpool beteiligt ist
    liverpool_matches = matches[
        (matches.home_team == 'Liverpool') | (matches.away_team == 'Liverpool')
    ]

    # Selektiere nur relevante Spalten
    liverpool_matches = liverpool_matches[['match_id', 'match_date', 'home_team', 'away_team', 'home_score', 'away_score']]
    
    # Ergebnis Formatierung
    liverpool_matches['result'] = liverpool_matches.apply(
        lambda x: f"{x['home_team']} {x['home_score']} - {x['away_score']} {x['away_team']}", axis=1
    )

    # Ausgabe der relevanten Informationen
    print("Liverpool Matches in the 18/19 Premier League Season:")
    for _, row in liverpool_matches.iterrows():
        print(f"{row['match_date']}: {row['result']} (Home: {row['home_team']} - Away: {row['away_team']})")

# Funktion aufrufen mit der spezifischen Saison-ID für 18/19 PL Saison
fetch_liverpool_matches(4)  # Der Season-Code für die PL Saison 2018/19 könnte je nach API unterschiedlich sein.
