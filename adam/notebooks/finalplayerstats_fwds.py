import pandas as pd
import numpy as np

# Funktion zum Laden der Daten und Entfernen doppelter Einträge
def update_csv(file_path):
    """Lädt die CSV-Datei, entfernt doppelte Einträge und speichert die aktualisierte Datei."""
    df = pd.read_csv(file_path)
    # Entfernen von doppelten Einträgen basierend auf 'Player', 'Nation' und 'Pos'
    df = df.drop_duplicates(subset=['Player', 'Nation', 'Pos'])
    # Aktualisieren der CSV-Datei
    df.to_csv(file_path, index=False)
    print(f"Updated CSV file: {file_path}")

# Funktion zur Berechnung der per90-Statistiken
def calculate_per90_stats(fw_players, stats_to_convert):
    """Berechnet die per90-Werte für die angegebenen Statistiken."""
    for stat in stats_to_convert:
        fw_players[stat + '_per90'] = fw_players[stat] / fw_players['Min'] * 90
    return fw_players

# Funktion zur Berechnung des Perzentilrangs
def calculate_percentile(player_value, all_values):
    """Berechnet den Perzentilrang eines Wertes in einer Liste von Werten."""
    return np.sum(all_values < player_value) / len(all_values) * 100

# Funktion zur Berechnung der Perzentile für alle Spieler und Speichern in einer neuen CSV
def calculate_and_save_percentiles(file_path, output_path, stats_to_convert, extra_stats):
    """Lädt die CSV-Datei, filtert Spieler, berechnet per90-Statistiken und speichert die Perzentile in einer neuen CSV."""
    df = pd.read_csv(file_path)
    fw_players = df[(df['Pos'] == 'FW') & (df['Min'] >= 300)]
    fw_players = calculate_per90_stats(fw_players, stats_to_convert)
    
    # Neue DataFrame zur Speicherung der Perzentile
    percentile_df = pd.DataFrame(columns=['Player', 'Club', 'Nation', 'Pos', 'Age', 'Minutes'] + [
        'Goals without penalties', 'Assists', 'Expected goals', 'Expected assists', 'Progressive runs',
        'Shot creating actions', 'Crosses into penalty area', 'Successful Take-ons', 
        'Goals per shots on target', 'Shots on target %', 'Shots', 'Aerial duels won'
    ])
    
    for player_id in fw_players.index:
        player_data = fw_players.loc[player_id, ['Player', 'Club', 'Nation', 'Pos', 'Age', 'Min']].tolist()
        player_percentiles = []

        for stat in stats_to_convert:
            stat_per90 = stat + '_per90'
            player_value = fw_players.loc[player_id, stat_per90]
            player_percentiles.append(calculate_percentile(player_value, fw_players[stat_per90]))

        for stat in extra_stats:
            player_value = fw_players.loc[player_id, stat]
            player_percentiles.append(calculate_percentile(player_value, fw_players[stat]))

        # Zusammenfügen der Spielerinformationen und Perzentile
        player_row = player_data + player_percentiles
        percentile_df.loc[len(percentile_df)] = player_row

    # Speichern der Perzentile in einer neuen CSV-Datei
    percentile_df.to_csv(output_path, index=False)
    print(f"Saved percentiles to: {output_path}")

if __name__ == "__main__":
    # Datei-Pfad zur ursprünglichen CSV-Datei
    file_path = 'merged_t5_players.csv'
    
    # Datei-Pfad zur Ausgabe-CSV-Datei
    output_path = 'players_percentiles.csv'

    # Aktualisieren der CSV-Datei, um doppelte Einträge zu entfernen
    update_csv(file_path)

    # Statistiken, die zu per90 umgerechnet werden müssen
    stats_to_convert = ['G-PK', 'Ast', 'xG', 'xAG', 'PrgR']
    
    # Zusätzliche Statistiken
    extra_stats = ['SCA90', 'CrsPA', 'Succ%', 'G/SoT', 'SoT%', 'Sh/90', 'Won%']

    # Berechnung der Perzentile und Speicherung in einer neuen CSV-Datei
    calculate_and_save_percentiles(file_path, output_path, stats_to_convert, extra_stats)
