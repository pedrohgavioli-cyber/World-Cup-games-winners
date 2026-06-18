import pandas as pd
import numpy as np

def obter_estatisticas_historicas(caminho_arquivo='results.csv'):

    dados = pd.read_csv(caminho_arquivo)

    dados = dados[['home_team', 'away_team', 'home_score', 'away_score', 'date']]
    dados['date'] = pd.to_datetime(dados['date'])
    dados = dados.loc[~dados['home_score'].isna() & ~dados['away_score'].isna()]

    dados_confrontos = dados.copy()

    dados_confrontos['time1'] = np.minimum(dados_confrontos['home_team'], dados_confrontos['away_team'])
    dados_confrontos['time2'] = np.maximum(dados_confrontos['home_team'], dados_confrontos['away_team'])

    dados_confrontos['gols_time1'] = np.where(
        dados_confrontos['home_team'] == dados_confrontos['time1'],
        dados_confrontos['home_score'],
        dados_confrontos['away_score']
    )

    dados_confrontos['gols_time2'] = np.where(
        dados_confrontos['home_team'] == dados_confrontos['time1'],
        dados_confrontos['away_score'],
        dados_confrontos['home_score']
    )

    # Cria colunas binárias (0 ou 1) para cada resultado possível
    dados_confrontos['vitoria_time1'] = (dados_confrontos['gols_time1'] > dados_confrontos['gols_time2']).astype(int)
    dados_confrontos['vitoria_time2'] = (dados_confrontos['gols_time1'] < dados_confrontos['gols_time2']).astype(int)
    dados_confrontos['empate'] = (dados_confrontos['gols_time1'] == dados_confrontos['gols_time2']).astype(int)

    confronto_media = (
        dados_confrontos
        .groupby(['time1', 'time2'])[['gols_time1', 'gols_time2', 'vitoria_time1', 'vitoria_time2', 'empate']]
        .mean()
        .reset_index()
    )
    return confronto_media

if __name__ == '__main__':
    estatisticas_historicas = obter_estatisticas_historicas()
    print(estatisticas_historicas.head())
