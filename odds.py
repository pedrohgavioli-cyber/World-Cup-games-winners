import requests
import pandas as pd

url = 'https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey=805fcc42035ee90840f0bdc5cb741c2b&regions={}&markets=h2h,spreads&oddsFormat=decimal'

regions = ['uk', 'us', 'eu', 'au'] # 'br' substituido por 'uk' pois 'br' nao e uma regiao valida na API

all_odds = []

for region in regions:
    url_with_region = url.format(region)

    try:
        response = requests.get(url_with_region)
        if response.status_code == 200:
            data = response.json()

            for match in data:
                match_info = {
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'commence_time': match['commence_time'],
                    'region': region
                }

                # Check if bookmakers exist
                if match.get('bookmakers'):
                    for bookmaker in match['bookmakers']:
                        for market in bookmaker['markets']:
                            if market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    if outcome['name'] == match['home_team']:
                                        match_info['home_odds'] = outcome['price']
                                    elif outcome['name'] == match['away_team']:
                                        match_info['away_odds'] = outcome['price']

                all_odds.append(match_info)
        else:
            print(f"Erro ao buscar dados para a região {region}: Status code {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para a região {region}: {e}")

if all_odds:
    df = pd.DataFrame(all_odds)
    print("Dados coletados:")
    print(df.head())
else:
    print("Nenhum dado foi coletado.")
