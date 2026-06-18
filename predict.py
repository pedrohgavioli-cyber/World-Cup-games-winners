import pandas as pd
import numpy as np
from data import get_historical_stats
from odds import get_upcoming_matches

def predict_winners(historical_stats, upcoming_matches):

    predictions = []

    for index, match in upcoming_matches.iterrows():
        home_team, away_team = match['game'].split(' vs ')

        # Para encontrar o histórico, normalizamos a ordem dos times
        team1 = min(home_team, away_team)
        team2 = max(home_team, away_team)

        # Busca o histórico do confronto
        matchup_history = historical_stats[
            (historical_stats['team1'] == team1) &
            (historical_stats['team2'] == team2)
        ]

        prediction = "Sem dados históricos"
        if not matchup_history.empty:
            hist_goals_team1 = matchup_history['goals_team1'].iloc[0]
            hist_goals_team2 = matchup_history['goals_team2'].iloc[0]

            # Determina qual time histórico corresponde ao time da casa/visitante
            if team1 == home_team:
                avg_goals_home = hist_goals_team1
                avg_goals_away = hist_goals_team2
            else:
                avg_goals_home = hist_goals_team2
                avg_goals_away = hist_goals_team1

            # Lógica de previsão simples: quem marcou mais gols em média?
            if avg_goals_home > avg_goals_away:
                prediction = home_team
            elif avg_goals_away > avg_goals_home:
                prediction = away_team
            else:
                prediction = "Empate (baseado na média de gols)"
        
        predictions.append({
            'game': match['game'],
            'commence_time': match['commence_time'],
            'avg_home_odds': match['avg_home_odds'],
            'avg_away_odds': match['avg_away_odds'],
            'predicted_winner': prediction
        })

    return pd.DataFrame(predictions)

if __name__ == '__main__':
    print("Buscando dados históricos...")
    historical_data = get_historical_stats('results.csv')

    print("Buscando próximas partidas e odds...")
    upcoming_games = get_upcoming_matches()

    if not upcoming_games.empty:
        print("Gerando previsões...")
        final_predictions = predict_winners(historical_data, upcoming_games)
        print("\n--- Previsões das Partidas ---")
        print(final_predictions.to_string())
    else:
        print("\nNenhuma partida futura encontrada para prever.")