import re

def parse_fee(fee_str):
    fee_str = fee_str.strip()
    if '€' in fee_str:
        # Entferne nicht-numerische Zeichen, die nicht Punkt oder Buchstaben sind (für 'm' oder 'k')
        fee_str = re.sub(r'[^\d.mk]', '', fee_str)
        # Prüfe auf Millionen 'm' und konvertiere entsprechend
        if 'm' in fee_str:
            fee_str = fee_str.replace('m', '')
            try:
                return float(fee_str)  # Direkte Umwandlung, da bereits in Millionen
            except ValueError:
                return 0.0
        # Prüfe auf Tausend 'k' und konvertiere in Millionen
        elif 'k' in fee_str:
            fee_str = fee_str.replace('k', '')
            try:
                return float(fee_str) / 1000  # Umwandlung von Tausend in Millionen
            except ValueError:
                return 0.0
        else:
            return 0.0
    elif 'Loan fee' in fee_str:
        # Suche nach Zahlen und ob 'm' oder 'k' vorhanden ist
        loan_fee = re.search(r'€([\d.]+)(m|k)?', fee_str)
        if loan_fee:
            amount, unit = loan_fee.groups()
            if unit == 'm':
                return float(amount)
            elif unit == 'k':
                return float(amount) / 1000
            else:
                return 0.0
        else:
            return 0.0
    return 0.0  # Behandle alle anderen Fälle als 0

#########

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_transfer_data(season, vereins_id, team_name, heim=True):
    url = f'https://www.transfermarkt.com/{team_name.lower().replace(' ', '-')}/transfers/verein/{vereins_id}/saison_id/{season}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    transfer_tables = soup.find_all('table', class_='items')
    if heim:
        transfer_table = transfer_tables[0] if transfer_tables else None
    else:
        transfer_table = transfer_tables[1] if len(transfer_tables) > 1 else None
    
    if not transfer_table:
        return pd.DataFrame()  # return an empty DataFrame if no table found
    
    rows = transfer_table.find_all('tr', class_=['odd', 'even'])
    transfers = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 3:
            player_info = cols[1].text.split(' \n\n\n')
            player_position = player_info[2].strip() if player_info else ""
            player_name = player_info[1].strip() if len(player_info) > 1 else ""
            transfer_fee = parse_fee(cols[11].text.strip())
            tag = ""
            if heim:
                tag = "Arrival"
            else:
                tag = "Departure"
            season_name = str(season) + "/" + str(season + 1)
            transfers.append({'Player': player_name, "Team": team_name, 'Position': player_position, 'Fee': transfer_fee, "Season": season_name, "Transfer": tag})
    
    return pd.DataFrame(transfers)

def scrape_all_seasons(start_season, end_season, vereins_id, team_name, heim=True):
    all_transfers = pd.DataFrame()
    
    for season in range(start_season, end_season + 1):
        season_transfers = scrape_transfer_data(season, vereins_id, team_name, heim)
        all_transfers = pd.concat([all_transfers, season_transfers], ignore_index=True)
    
    return all_transfers

# Collect all transfers into a single DataFrame
all_transfers = pd.DataFrame()

clubs = [
    (31, "Liverpool"),
    (985, "Manchester United"),
    (631, "Chelsea"),
    (11, "Arsenal"),
    (148, "Tottenham Hotspur"),
    (281, "Manchester City")
]

for club_id, club_name in clubs:
    club_transfers = scrape_all_seasons(2012, 2018, club_id, club_name)
    all_transfers = pd.concat([all_transfers, club_transfers], ignore_index=True)
    club_transfers = scrape_all_seasons(2012, 2018, club_id, club_name, False)
    all_transfers = pd.concat([all_transfers, club_transfers], ignore_index=True)

# all_transfers now contains the transfer data of all clubs from 2012 to 2022

#########

# write a sciprt which plots a barplot with departures and arrivals of each club in the 2818/2019 season with plotly
import plotly.graph_objs as go
import plotly.express as px

season_2018_2019 = all_transfers[all_transfers["Season"] == "2018/2019"]
fig = px.bar(season_2018_2019, x="Team", y="Fee", color="Transfer", barmode="group", title="Transfer fees of Premier League clubs in 2018/2019 season")
fig.show()