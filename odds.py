import requests
import pandas as pd
import numpy as np

def obter_proximas_partidas():
    
    CHAVE_API = '805fcc42035ee90840f0bdc5cb741c2b'
    TEMPLATE_URL = 'https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={}&regions={}&markets=h2h,spreads&oddsFormat=decimal'
    REGIOES = ['br', 'us', 'eu', 'au']

    dados_partidas_unicas = {}

    for regiao in REGIOES:
        url_com_regiao = TEMPLATE_URL.format(CHAVE_API, regiao)
        try:
            resposta = requests.get(url_com_regiao)
            resposta.raise_for_status()
            dados = resposta.json()

            for partida in dados:
                id_partida = partida['id']
                if id_partida not in dados_partidas_unicas:
                    dados_partidas_unicas[id_partida] = {
                        'time_casa': partida['home_team'],
                        'time_visitante': partida['away_team'],
                        'horario_inicio': partida['commence_time'],
                        'casas_de_apostas': []
                    }
                dados_partidas_unicas[id_partida]['casas_de_apostas'].extend(partida['bookmakers'])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados para a região {regiao}: {e}")
            continue

    lista_odds_finais = []

    for id_partida, dados_partida in dados_partidas_unicas.items():
        lista_odds_casa = []
        lista_odds_visitante = []

        for casa_de_aposta in dados_partida['casas_de_apostas']:
            for mercado in casa_de_aposta['markets']:
                if mercado['key'] == 'h2h':
                    for resultado in mercado['outcomes']:
                        if resultado['name'] == dados_partida['time_casa']:
                            lista_odds_casa.append(resultado['price'])
                        elif resultado['name'] == dados_partida['time_visitante']:
                            lista_odds_visitante.append(resultado['price'])

        media_odds_casa = np.mean(lista_odds_casa) if lista_odds_casa else np.nan
        media_odds_visitante = np.mean(lista_odds_visitante) if lista_odds_visitante else np.nan

        info_partida = {
            'time_casa': dados_partida['time_casa'],
            'time_visitante': dados_partida['time_visitante'],
            'horario_inicio': dados_partida['horario_inicio'],
            'media_odds_casa': media_odds_casa,
            'media_odds_visitante': media_odds_visitante
        }
        lista_odds_finais.append(info_partida)


    df_todas_odds = pd.DataFrame(lista_odds_finais)
    if not df_todas_odds.empty:
        df_todas_odds['jogo'] = df_todas_odds['time_casa'] + ' vs ' + df_todas_odds['time_visitante']
        df_todas_odds.drop(['time_casa', 'time_visitante'], axis=1, inplace=True)
        df_todas_odds = df_todas_odds.sort_values(by='horario_inicio')
    return df_todas_odds

if __name__ == '__main__':
    proximas_partidas = obter_proximas_partidas()
    print(proximas_partidas.head())
