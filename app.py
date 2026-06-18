import streamlit as st
import pandas as pd
import numpy as np
from data import get_historical_stats
from odds import get_upcoming_matches
from predict import predict_winners 

def main():
    st.title("Previsão de Vencedores da Copa do Mundo")
    
    st.write("Buscando dados históricos...")
    historical_data = get_historical_stats('results.csv')

    st.subheader("Simular Confronto Específico")
    # Extrai os nomes únicos de todos os times para os selectboxes
    teams = list(pd.concat([historical_data['team1'], historical_data['team2']]).unique())
    teams.sort()
    
    banca = st.number_input("Sua Banca Atual (R$)", min_value=1.0, value=10000.0, step=1.0)

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Time 1 (Casa)", teams)
        odds1 = st.number_input("Odds Time 1 (Casa)", min_value=1.0, value=2.0, step=0.1)
    with col2:
        team2 = st.selectbox("Time 2 (Visitante)", teams)
        odds2 = st.number_input("Odds Time 2 (Visitante)", min_value=1.0, value=2.0, step=0.1)
        
    if st.button("Prever Confronto"):
        if team1 == team2:
            st.warning("Por favor, selecione times diferentes.")
        else:
            mock_match = pd.DataFrame([{
                'game': f"{team1} vs {team2}",
                'commence_time': 'Simulação',
                'avg_home_odds': odds1,
                'avg_away_odds': odds2
            }])
            prediction_df = predict_winners(historical_data, mock_match)
            
            winner = prediction_df['predicted_winner'].iloc[0]
            if winner == "Sem dados históricos":
                st.warning("Sem dados históricos para este confronto.")
            else:
                home_prob = prediction_df['home_prob'].iloc[0] * 100
                away_prob = prediction_df['away_prob'].iloc[0] * 100
                draw_prob = prediction_df['draw_prob'].iloc[0] * 100
                
                st.success(f"Vencedor Previsto: **{winner}**")
                st.info(f"**Probabilidades Históricas:**\n\n"
                        f"- Vitória do **{team1}**: {home_prob:.1f}%\n"
                        f"- **Empate**: {draw_prob:.1f}%\n"
                        f"- Vitória do **{team2}**: {away_prob:.1f}%")
                        
                suggested_bet = prediction_df['suggested_bet'].iloc[0]
                kelly_fraction = prediction_df['kelly_fraction'].iloc[0]
            
            st.success(f"**Análise de Aposta:** {suggested_bet}")
            if kelly_fraction > 0:
                stake = banca * kelly_fraction
                st.info(f"**Quantia Sugerida a Apostar (Stake):** R$ {stake:.2f}")

    st.markdown("---")
    st.subheader("Próximas Partidas Oficiais (API de Odds)")
    st.write("Buscando próximas partidas e odds...")
    upcoming_games = get_upcoming_matches()

    if not upcoming_games.empty:
        predictions_df = predict_winners(historical_data, upcoming_games)
        st.write("Previsões para as próximas partidas:")
        
        # Formata as probabilidades para exibição no DataFrame
        display_df = predictions_df.copy()
        display_df['home_prob'] = (display_df['home_prob'] * 100).apply(lambda x: f"{x:.1f}%")
        display_df['away_prob'] = (display_df['away_prob'] * 100).apply(lambda x: f"{x:.1f}%")
        display_df['draw_prob'] = (display_df['draw_prob'] * 100).apply(lambda x: f"{x:.1f}%")
        
        # Removemos a coluna kelly_fraction da tabela para não poluir
        display_df = display_df.drop(columns=['kelly_fraction'])
        
        st.dataframe(display_df)
    else:
        st.write("Nenhuma partida futura encontrada.")

if __name__ == '__main__':
    main()

# streamlit run app.py