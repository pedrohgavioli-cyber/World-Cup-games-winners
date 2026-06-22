import pandas as pd
import numpy as np
from datetime import datetime

def calcular_pesos_tempo(datas: pd.Series, meia_vida_dias: int = 365 * 3) -> pd.Series:
    """
    Calcula pesos com base no decaimento exponencial (Time Decay).
    Partidas mais recentes recebem peso maior.

    Args:
        datas (pd.Series): Série pandas com as datas das partidas.
        meia_vida_dias (int): Dias necessários para o peso cair pela metade.

    Returns:
        pd.Series: Pesos calculados.
    """
    data_atual = pd.to_datetime('today')
    dias_passados = (data_atual - datas).dt.days
    # Garante que não tenhamos dias negativos se houver datas no futuro (improvável)
    dias_passados = np.maximum(dias_passados, 0)

    # Decaimento exponencial: peso = e^(-lambda * tempo)
    # lambda = ln(2) / meia_vida
    taxa_decaimento = np.log(2) / meia_vida_dias
    pesos = np.exp(-taxa_decaimento * dias_passados)

    return pesos

def preparar_estatisticas_equipes(caminho_arquivo: str = 'results.csv') -> dict:
    """
    Processa a base histórica e calcula a Força de Ataque e Defesa
    de cada seleção, considerando o Time Decay e a média global do torneio.

    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV com resultados.

    Returns:
        dict: Dicionário contendo as forças das equipes e a média global de gols.
    """
    # Carregar os dados
    df = pd.read_csv(caminho_arquivo)

    # Limpeza básica
    df = df[['date', 'home_team', 'away_team', 'home_score', 'away_score']].dropna()
    df['date'] = pd.to_datetime(df['date'])

    # Calcular os pesos de tempo para cada partida
    df['peso'] = calcular_pesos_tempo(df['date'])

    # Média global de gols no torneio (ponderada)
    # Gols da casa e visitante
    total_peso = df['peso'].sum()
    media_gols_casa = (df['home_score'] * df['peso']).sum() / total_peso
    media_gols_visitante = (df['away_score'] * df['peso']).sum() / total_peso

    media_global = {
        'casa': media_gols_casa,
        'visitante': media_gols_visitante
    }

    # Agregar estatísticas por time mandante
    stats_casa = df.groupby('home_team').apply(
        lambda x: pd.Series({
            'gols_marcados_ponderados': (x['home_score'] * x['peso']).sum(),
            'gols_sofridos_ponderados': (x['away_score'] * x['peso']).sum(),
            'peso_total_casa': x['peso'].sum()
        })
    ).reset_index().rename(columns={'home_team': 'time'})

    # Agregar estatísticas por time visitante
    stats_visitante = df.groupby('away_team').apply(
        lambda x: pd.Series({
            'gols_marcados_ponderados': (x['away_score'] * x['peso']).sum(),
            'gols_sofridos_ponderados': (x['home_score'] * x['peso']).sum(),
            'peso_total_visitante': x['peso'].sum()
        })
    ).reset_index().rename(columns={'away_team': 'time'})

    # Combinar estatísticas
    stats_gerais = pd.merge(stats_casa, stats_visitante, on='time', how='outer', suffixes=('_casa', '_visitante')).fillna(0)

    stats_gerais['peso_total'] = stats_gerais['peso_total_casa'] + stats_gerais['peso_total_visitante']

    # Média de gols marcados e sofridos por time (ponderada)
    stats_gerais['media_marcados_casa'] = np.where(
        stats_gerais['peso_total_casa'] > 0,
        stats_gerais['gols_marcados_ponderados_casa'] / stats_gerais['peso_total_casa'],
        media_gols_casa
    )
    stats_gerais['media_sofridos_casa'] = np.where(
        stats_gerais['peso_total_casa'] > 0,
        stats_gerais['gols_sofridos_ponderados_casa'] / stats_gerais['peso_total_casa'],
        media_gols_visitante
    )

    stats_gerais['media_marcados_visitante'] = np.where(
        stats_gerais['peso_total_visitante'] > 0,
        stats_gerais['gols_marcados_ponderados_visitante'] / stats_gerais['peso_total_visitante'],
        media_gols_visitante
    )
    stats_gerais['media_sofridos_visitante'] = np.where(
        stats_gerais['peso_total_visitante'] > 0,
        stats_gerais['gols_sofridos_ponderados_visitante'] / stats_gerais['peso_total_visitante'],
        media_gols_casa
    )

    # Força de Ataque = Média de gols marcados do time / Média de gols do torneio
    stats_gerais['forca_ataque_casa'] = stats_gerais['media_marcados_casa'] / media_gols_casa
    stats_gerais['forca_ataque_visitante'] = stats_gerais['media_marcados_visitante'] / media_gols_visitante

    # Força de Defesa = Média de gols sofridos do time / Média de gols do torneio
    stats_gerais['forca_defesa_casa'] = stats_gerais['media_sofridos_casa'] / media_gols_visitante
    stats_gerais['forca_defesa_visitante'] = stats_gerais['media_sofridos_visitante'] / media_gols_casa

    # Ajustando eventuais valores extremos para equipes com poucos jogos
    for col in ['forca_ataque_casa', 'forca_ataque_visitante', 'forca_defesa_casa', 'forca_defesa_visitante']:
        stats_gerais[col] = stats_gerais[col].clip(lower=0.1, upper=5.0)

    # Converter para dicionário para acesso rápido
    forcas_equipes = {}
    for _, row in stats_gerais.iterrows():
        forcas_equipes[row['time']] = {
            'forca_ataque_casa': row['forca_ataque_casa'],
            'forca_defesa_casa': row['forca_defesa_casa'],
            'forca_ataque_visitante': row['forca_ataque_visitante'],
            'forca_defesa_visitante': row['forca_defesa_visitante']
        }

    return {
        'media_global': media_global,
        'forcas_equipes': forcas_equipes
    }

if __name__ == '__main__':
    resultado = preparar_estatisticas_equipes('results.csv')
    print("Média global do torneio:", resultado['media_global'])
    print("Forças do Brasil:", resultado['forcas_equipes'].get('Brazil'))
