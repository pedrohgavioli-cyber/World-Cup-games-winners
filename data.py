import pandas as pd
import numpy as np

def get_historical_stats(file_path='results.csv'):

    data = pd.read_csv(file_path)

    data = data[['home_team', 'away_team', 'home_score', 'away_score', 'date']]
    data['date'] = pd.to_datetime(data['date'])
    data = data.loc[~data['home_score'].isna() & ~data['away_score'].isna()]

    data_matchups = data.copy()

    data_matchups['team1'] = np.minimum(data_matchups['home_team'], data_matchups['away_team'])
    data_matchups['team2'] = np.maximum(data_matchups['home_team'], data_matchups['away_team'])

    data_matchups['goals_team1'] = np.where(
        data_matchups['home_team'] == data_matchups['team1'],
        data_matchups['home_score'],
        data_matchups['away_score']
    )

    data_matchups['goals_team2'] = np.where(
        data_matchups['home_team'] == data_matchups['team1'],
        data_matchups['away_score'],
        data_matchups['home_score']
    )

    confronto_media = (
        data_matchups
        .groupby(['team1', 'team2'])[['goals_team1', 'goals_team2']]
        .mean()
        .reset_index()
    )
    return confronto_media

if __name__ == '__main__':
    historical_stats = get_historical_stats()
    print(historical_stats.head())
