import requests
import pandas as pd
url = 'https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey=805fcc42035ee90840f0bdc5cb741c2b&regions={}&markets=h2h,spreads&oddsFormat=decimal'
regions = ['br', 'us', 'eu', 'au']

all_odds = []

for region in regions:
  # accumulate odds across regions instead of reinitializing
  url_with_region = url.format(region)
  response = requests.get(url_with_region)
  if response.status_code == 200:
      data = response.json()
      
      for match in data:
          match_info = {
              'home_team': match['home_team'],
              'away_team': match['away_team'],
              'commence_time': match['commence_time']
          }
          
          for bookmaker in match['bookmakers']:
              for market in bookmaker['markets']:
                  if market['key'] == 'h2h':
                      for outcome in market['outcomes']:
                          if outcome['name'] == match['home_team']:
                              match_info['home_odds'] = outcome['price']
                          elif outcome['name'] == match['away_team']:
                              match_info['away_odds'] = outcome['price']
          
          all_odds.append(match_info)
all_odds_df = pd.DataFrame(all_odds)
print(all_odds_df)