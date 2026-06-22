import pandas as pd
import numpy as np
import json
from data_prep import preparar_estatisticas_equipes
from poisson_model import calcular_probabilidades_partida
from odds import obter_proximas_partidas

def prever_vencedores(dados_modelo: dict, proximas_partidas: pd.DataFrame) -> pd.DataFrame:
    """
    Preve os vencedores e probabilidades usando o modelo de Poisson.

    Args:
        dados_modelo (dict): Estatísticas e médias geradas pelo data_prep.py.
        proximas_partidas (pd.DataFrame): DataFrame com as próximas partidas.

    Returns:
        pd.DataFrame: DataFrame contendo as previsões.
    """
    media_global = dados_modelo['media_global']
    forcas_equipes = dados_modelo['forcas_equipes']

    previsoes = []

    for indice, partida in proximas_partidas.iterrows():
        time_casa, time_visitante = partida['jogo'].split(' vs ')

        if time_casa in forcas_equipes and time_visitante in forcas_equipes:
            forca_ataque_casa = forcas_equipes[time_casa]['forca_ataque_casa']
            forca_defesa_casa = forcas_equipes[time_casa]['forca_defesa_casa']
            
            forca_ataque_visitante = forcas_equipes[time_visitante]['forca_ataque_visitante']
            forca_defesa_visitante = forcas_equipes[time_visitante]['forca_defesa_visitante']

            # Calcular probabilidades via Poisson
            resultado_poisson = calcular_probabilidades_partida(
                forca_ataque_casa, forca_defesa_casa,
                forca_ataque_visitante, forca_defesa_visitante,
                media_global
            )

            prob_casa = resultado_poisson['prob_vitoria_casa']
            prob_visitante = resultado_poisson['prob_vitoria_visitante']
            prob_empate = resultado_poisson['prob_empate']
            xg_casa = resultado_poisson['xg_casa']
            xg_visitante = resultado_poisson['xg_visitante']
            placares_provaveis = resultado_poisson['placares_mais_provaveis']

            # Determinar a previsão
            if prob_casa > prob_visitante and prob_casa > prob_empate:
                previsao = time_casa
            elif prob_visitante > prob_casa and prob_visitante > prob_empate:
                previsao = time_visitante
            else:
                previsao = "Empate"

        else:
            previsao = "Sem dados históricos"
            prob_casa = 0.0
            prob_visitante = 0.0
            prob_empate = 0.0
            xg_casa = 0.0
            xg_visitante = 0.0
            placares_provaveis = []
        
        # Lógica de aposta sugerida (Valor Esperado)
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
            'xg_casa': xg_casa,
            'xg_visitante': xg_visitante,
            'aposta_sugerida': aposta_sugerida,
            'fracao_kelly': fracao_kelly,
            'placares_provaveis': placares_provaveis
        })

    return pd.DataFrame(previsoes)

if __name__ == '__main__':
    print("Iniciando Módulo de Engenharia de Dados...")
    dados_modelo = preparar_estatisticas_equipes('results.csv')

    print("Simulando uma partida de teste: Brasil vs Argentina")
    partida_teste = pd.DataFrame([{
        'jogo': 'Brazil vs Argentina',
        'horario_inicio': 'Agora',
        'media_odds_casa': 2.50,
        'media_odds_visitante': 3.10
    }])

    previsao_teste = prever_vencedores(dados_modelo, partida_teste)

    # Exportar para JSON (preparando terreno para API)
    resultado_json = previsao_teste.to_dict(orient='records')
    print("\nResultado da Previsão (Formato JSON):")
    print(json.dumps(resultado_json, indent=4, ensure_ascii=False))
