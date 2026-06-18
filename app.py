import streamlit as st
import pandas as pd
import numpy as np
from data import obter_estatisticas_historicas
from odds import obter_proximas_partidas
from predict import prever_vencedores

def main():
    st.title("Previsão de Vencedores da Copa do Mundo")
    
    st.write("Buscando dados históricos...")
    dados_historicos = obter_estatisticas_historicas('results.csv')

    st.subheader("Simular Confronto Específico")
    # Extrai os nomes únicos de todos os times para os selectboxes
    times = pd.concat([dados_historicos['time1'], dados_historicos['time2']]).unique().tolist()
    times.sort()
    
    banca = st.number_input("Sua Banca Atual (R$)", min_value=1.0, value=10000.0, step=1.0)

    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.selectbox("Time 1 (Casa)", times)
        odds_casa = st.number_input("Odds Time 1 (Casa)", min_value=1.0, value=2.0, step=0.1)
    with col2:
        time_visitante = st.selectbox("Time 2 (Visitante)", times)
        odds_visitante = st.number_input("Odds Time 2 (Visitante)", min_value=1.0, value=2.0, step=0.1)
        
    if st.button("Prever Confronto"):
        if time_casa == time_visitante:
            st.warning("Por favor, selecione times diferentes.")
        else:
            simulacao_partida = pd.DataFrame([{
                'jogo': f"{time_casa} vs {time_visitante}",
                'horario_inicio': 'Simulação',
                'media_odds_casa': odds_casa,
                'media_odds_visitante': odds_visitante
            }])
            df_previsao = prever_vencedores(dados_historicos, simulacao_partida)
            
            vencedor = df_previsao['vencedor_previsto'].iloc[0]
            if vencedor == "Sem dados históricos":
                st.warning("Sem dados históricos para este confronto.")
            else:
                prob_casa_pct = df_previsao['prob_casa'].iloc[0] * 100
                prob_visitante_pct = df_previsao['prob_visitante'].iloc[0] * 100
                prob_empate_pct = df_previsao['prob_empate'].iloc[0] * 100
                
                st.success(f"Vencedor Previsto: **{vencedor}**")
                st.info(f"**Probabilidades Históricas:**\n\n"
                        f"- Vitória do **{time_casa}**: {prob_casa_pct:.1f}%\n"
                        f"- **Empate**: {prob_empate_pct:.1f}%\n"
                        f"- Vitória do **{time_visitante}**: {prob_visitante_pct:.1f}%")
                        
                aposta_sugerida = df_previsao['aposta_sugerida'].iloc[0]
                fracao_kelly = df_previsao['fracao_kelly'].iloc[0]
            
                st.success(f"**Análise de Aposta:** {aposta_sugerida}")
                if fracao_kelly > 0:
                    stake = banca * fracao_kelly
                    st.info(f"**Quantia Sugerida a Apostar (Stake):** R$ {stake:.2f}")

    st.markdown("---")
    st.subheader("Próximas Partidas Oficiais (API de Odds)")
    st.write("Buscando próximas partidas e odds...")
    proximos_jogos = obter_proximas_partidas()

    if not proximos_jogos.empty:
        df_previsoes_finais = prever_vencedores(dados_historicos, proximos_jogos)
        st.write("Previsões para as próximas partidas:")
        
        # Formata as probabilidades para exibição no DataFrame
        df_exibicao = df_previsoes_finais.copy()
        df_exibicao['prob_casa'] = (df_exibicao['prob_casa'] * 100).apply(lambda x: f"{x:.1f}%")
        df_exibicao['prob_visitante'] = (df_exibicao['prob_visitante'] * 100).apply(lambda x: f"{x:.1f}%")
        df_exibicao['prob_empate'] = (df_exibicao['prob_empate'] * 100).apply(lambda x: f"{x:.1f}%")
        
        # Removemos a coluna fracao_kelly da tabela para não poluir
        df_exibicao = df_exibicao.drop(columns=['fracao_kelly'])
        
        # Renomeando as colunas para o Português para a tabela exibida no Streamlit
        df_exibicao = df_exibicao.rename(columns={
            'jogo': 'Jogo',
            'horario_inicio': 'Horário de Início',
            'media_odds_casa': 'Média Odds Casa',
            'media_odds_visitante': 'Média Odds Visitante',
            'vencedor_previsto': 'Vencedor Previsto',
            'prob_casa': 'Probabilidade Casa',
            'prob_visitante': 'Probabilidade Visitante',
            'prob_empate': 'Probabilidade Empate',
            'aposta_sugerida': 'Aposta Sugerida'
        })

        st.dataframe(df_exibicao)
    else:
        st.write("Nenhuma partida futura encontrada.")

if __name__ == '__main__':
    main()

# streamlit run app.py
