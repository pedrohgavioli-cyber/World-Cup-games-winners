import pandas as pd
import numpy as np
from data import obter_estatisticas_historicas
from odds import obter_proximas_partidas

def prever_vencedores(estatisticas_historicas, proximas_partidas):

    previsoes = []

    for indice, partida in proximas_partidas.iterrows():
        time_casa, time_visitante = partida['jogo'].split(' vs ')

        # Para encontrar o histórico, normalizamos a ordem dos times
        time1 = min(time_casa, time_visitante)
        time2 = max(time_casa, time_visitante)

        # Busca o histórico do confronto
        historico_confronto = estatisticas_historicas[
            (estatisticas_historicas['time1'] == time1) &
            (estatisticas_historicas['time2'] == time2)
        ]

        previsao = "Sem dados históricos"
        prob_casa = 0.0
        prob_visitante = 0.0
        prob_empate = 0.0

        if not historico_confronto.empty:
            hist_vitoria_time1 = historico_confronto['vitoria_time1'].iloc[0]
            hist_vitoria_time2 = historico_confronto['vitoria_time2'].iloc[0]
            hist_empate = historico_confronto['empate'].iloc[0]

            # Determina qual time histórico corresponde ao time da casa/visitante
            if time1 == time_casa:
                prob_casa = hist_vitoria_time1
                prob_visitante = hist_vitoria_time2
            else:
                prob_casa = hist_vitoria_time2
                prob_visitante = hist_vitoria_time1
            
            prob_empate = hist_empate

            # Lógica de previsão baseada no resultado histórico mais frequente
            if prob_casa > prob_visitante and prob_casa > prob_empate:
                previsao = time_casa
            elif prob_visitante > prob_casa and prob_visitante > prob_empate:
                previsao = time_visitante
            elif prob_empate > prob_casa and prob_empate > prob_visitante:
                previsao = "Empate"
            else:
                previsao = "Empate (probabilidades iguais)"
        
        # Lógica do sugeridor de apostas (Valor Esperado / Expected Value)
        aposta_sugerida = "Sem dados de odds"
        fracao_kelly = 0.0

        if not np.isnan(partida['media_odds_casa']) and not np.isnan(partida['media_odds_visitante']):
            ev_casa = (prob_casa * partida['media_odds_casa']) - 1
            ev_visitante = (prob_visitante * partida['media_odds_visitante']) - 1
            
            if ev_casa > 0 and ev_casa >= ev_visitante:
                fracao_kelly = ev_casa / (partida['media_odds_casa'] - 1)
                aposta_sugerida = f"Apostar: {time_casa} (EV: +{ev_casa*100:.1f}% | Kelly: {fracao_kelly*100:.1f}%)"

            elif ev_visitante > 0 and ev_visitante > ev_casa:
                fracao_kelly = ev_visitante / (partida['media_odds_visitante'] - 1)
                aposta_sugerida = f"Apostar: {time_visitante} (EV: +{ev_visitante*100:.1f}% | Kelly: {fracao_kelly*100:.1f}%)"
            else:
                aposta_sugerida = "Nenhuma aposta de valor"

        previsoes.append({
            'jogo': partida['jogo'],
            'horario_inicio': partida['horario_inicio'],
            'media_odds_casa': partida['media_odds_casa'],
            'media_odds_visitante': partida['media_odds_visitante'],
            'vencedor_previsto': previsao,
            'prob_casa': prob_casa,
            'prob_visitante': prob_visitante,
            'prob_empate': prob_empate,
            'aposta_sugerida': aposta_sugerida,
            'fracao_kelly': fracao_kelly
        })

    return pd.DataFrame(previsoes)

if __name__ == '__main__':
    print("Buscando dados históricos...")
    dados_historicos = obter_estatisticas_historicas('results.csv')

    print("Buscando próximas partidas e odds...")
    proximos_jogos = obter_proximas_partidas()

    if not proximos_jogos.empty:
        print("Gerando previsões...")
        previsoes_finais = prever_vencedores(dados_historicos, proximos_jogos)
        print("\n--- Previsões das Partidas ---")
        print(previsoes_finais.to_string())
    else:
        print("\nNenhuma partida futura encontrada para prever.")
