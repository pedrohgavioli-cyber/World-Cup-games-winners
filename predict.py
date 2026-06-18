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
        home_prob = 0.0
        away_prob = 0.0
        draw_prob = 0.0

        if not matchup_history.empty:
            hist_team1_win = matchup_history['team1_win'].iloc[0]
            hist_team2_win = matchup_history['team2_win'].iloc[0]
            hist_draw = matchup_history['draw'].iloc[0]

            # Determina qual time histórico corresponde ao time da casa/visitante
            if team1 == home_team:
                home_prob = hist_team1_win
                away_prob = hist_team2_win
            else:
                home_prob = hist_team2_win
                away_prob = hist_team1_win
            
            draw_prob = hist_draw

            # Lógica de previsão baseada no resultado histórico mais frequente
            if home_prob > away_prob and home_prob > draw_prob:
                prediction = home_team
            elif away_prob > home_prob and away_prob > draw_prob:
                prediction = away_team
            elif draw_prob > home_prob and draw_prob > away_prob:
                prediction = "Empate"
            else:
                prediction = "Empate (probabilidades iguais)"
        
        # Lógica do sugeridor de apostas (Valor Esperado / Expected Value)
        suggested_bet = "Sem dados de odds"
        kelly_fraction = 0.0

        if not np.isnan(match['avg_home_odds']) and not np.isnan(match['avg_away_odds']):
            home_ev = (home_prob * match['avg_home_odds']) - 1
            away_ev = (away_prob * match['avg_away_odds']) - 1
            
            if home_ev > 0 and home_ev >= away_ev:
                kelly_fraction = home_ev / (match['avg_home_odds'] - 1)
                suggested_bet = f"Apostar: {home_team} (EV: +{home_ev*100:.1f}% | Kelly: {kelly_fraction*100:.1f}%)"

            elif away_ev > 0 and away_ev > home_ev:
                kelly_fraction = away_ev / (match['avg_away_odds'] - 1)
                suggested_bet = f"Apostar: {away_team} (EV: +{away_ev*100:.1f}% | Kelly: {kelly_fraction*100:.1f}%)"
            else:
                suggested_bet = "Nenhuma aposta de valor"

        predictions.append({
            'game': match['game'],
            'commence_time': match['commence_time'],
            'avg_home_odds': match['avg_home_odds'],
            'avg_away_odds': match['avg_away_odds'],
            'predicted_winner': prediction,
            'home_prob': home_prob,
            'away_prob': away_prob,
            'draw_prob': draw_prob,
            'suggested_bet': suggested_bet,
            'kelly_fraction': kelly_fraction
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