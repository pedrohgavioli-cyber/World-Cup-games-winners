import numpy as np
from scipy.stats import poisson

def calcular_probabilidades_partida(forca_ataque_A: float, forca_defesa_A: float,
                                    forca_ataque_B: float, forca_defesa_B: float,
                                    media_torneio: dict, max_gols: int = 6) -> dict:
    """
    Calcula o xG de cada time e usa a distribuição de Poisson para
    gerar probabilidades de placares e resultados da partida.

    Args:
        forca_ataque_A (float): Força de ataque do time da casa.
        forca_defesa_A (float): Força de defesa do time da casa.
        forca_ataque_B (float): Força de ataque do time visitante.
        forca_defesa_B (float): Força de defesa do time visitante.
        media_torneio (dict): Dicionário com 'casa' e 'visitante' contendo as médias de gols.
        max_gols (int): Número máximo de gols para calcular probabilidades.

    Returns:
        dict: Dicionário contendo as probabilidades de vitória/empate e os placares mais prováveis.
    """
    # Cálculo do xG (Expected Goals - Lambda da distribuição de Poisson)
    # xG Casa = Força Ataque Casa * Força Defesa Visitante * Média Gols Casa Torneio
    xg_A = forca_ataque_A * forca_defesa_B * media_torneio['casa']

    # xG Visitante = Força Ataque Visitante * Força Defesa Casa * Média Gols Visitante Torneio
    xg_B = forca_ataque_B * forca_defesa_A * media_torneio['visitante']

    # Gerar vetores de probabilidade para número de gols (0 a max_gols)
    gols = np.arange(0, max_gols + 1)
    prob_A = poisson.pmf(gols, xg_A)
    prob_B = poisson.pmf(gols, xg_B)

    # Matriz bidimensional de probabilidades (Time A gols x Time B gols)
    # prob_matriz[i, j] = Prob(A marca i gols) * Prob(B marca j gols)
    prob_matriz = np.outer(prob_A, prob_B)

    # Probabilidades dos resultados (Vitória Casa, Empate, Vitória Visitante)
    prob_vitoria_A = np.tril(prob_matriz, -1).sum()
    prob_empate = np.trace(prob_matriz)
    prob_vitoria_B = np.triu(prob_matriz, 1).sum()

    # Extrair placares mais prováveis
    placares = []
    for i in range(max_gols + 1):
        for j in range(max_gols + 1):
            placares.append({
                'placar': f'{i}-{j}',
                'gols_casa': i,
                'gols_visitante': j,
                'probabilidade': float(prob_matriz[i, j])
            })

    # Ordenar placares decrescente por probabilidade
    placares.sort(key=lambda x: x['probabilidade'], reverse=True)
    placares_provaveis = placares[:3]

    return {
        'xg_casa': float(xg_A),
        'xg_visitante': float(xg_B),
        'prob_vitoria_casa': float(prob_vitoria_A),
        'prob_empate': float(prob_empate),
        'prob_vitoria_visitante': float(prob_vitoria_B),
        'placares_mais_provaveis': placares_provaveis
    }

if __name__ == '__main__':
    # Exemplo simples de teste
    media_torneio = {'casa': 1.45, 'visitante': 1.15}
    resultado = calcular_probabilidades_partida(1.2, 0.9, 1.1, 1.0, media_torneio)
    print("Previsão de Exemplo:")
    import json
    print(json.dumps(resultado, indent=4))
