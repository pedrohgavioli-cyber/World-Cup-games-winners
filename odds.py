import requests
import pandas as pd
import numpy as np

def get_upcoming_matches():
    
    API_KEY = '805fcc42035ee90840f0bdc5cb741c2b'
    URL_TEMPLATE = 'https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={}&regions={}&markets=h2h,spreads&oddsFormat=decimal'
    REGIONS = ['br', 'us', 'eu', 'au']

    unique_matches_data = {}

    for region in REGIONS:
        url_with_region = URL_TEMPLATE.format(API_KEY, region)
        try:
            response = requests.get(url_with_region)
            response.raise_for_status()
            data = response.json()

            for match in data:
                match_id = match['id']
                if match_id not in unique_matches_data:
                    unique_matches_data[match_id] = {
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'commence_time': match['commence_time'],
                        'bookmakers': []
                    }
                unique_matches_data[match_id]['bookmakers'].extend(match['bookmakers'])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados para a região {region}: {e}")
            continue

    final_odds_list = []

    for match_id, match_data in unique_matches_data.items():
        home_odds_list = []
        away_odds_list = []

        for bookmaker in match_data['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == match_data['home_team']:
                            home_odds_list.append(outcome['price'])
                        elif outcome['name'] == match_data['away_team']:
                            away_odds_list.append(outcome['price'])

        avg_home_odds = np.mean(home_odds_list) if home_odds_list else np.nan
        avg_away_odds = np.mean(away_odds_list) if away_odds_list else np.nan

        match_info = {
            'home_team': match_data['home_team'],
            'away_team': match_data['away_team'],
            'commence_time': match_data['commence_time'],
            'avg_home_odds': avg_home_odds,
            'avg_away_odds': avg_away_odds
        }
        final_odds_list.append(match_info)


    all_odds_df = pd.DataFrame(final_odds_list)
    all_odds_df['game'] = all_odds_df['home_team'] + ' vs ' + all_odds_df['away_team']
    all_odds_df.drop(['home_team', 'away_team'], axis=1, inplace=True)
    all_odds_df = all_odds_df.sort_values(by='commence_time')
    return all_odds_df

if __name__ == '__main__':
    upcoming_matches = get_upcoming_matches()
    print(upcoming_matches.head())
