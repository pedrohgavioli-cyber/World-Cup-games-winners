from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import time
from data import obter_estatisticas_historicas
from odds import obter_proximas_partidas
from predict import prever_vencedores

app = Flask(__name__)

# Simple cache implementation
cache = {
    'historical_data': None,
    'odds_data': None,
    'odds_last_fetch': 0
}

def get_historical_data_cached(file_path):
    if cache['historical_data'] is None:
        cache['historical_data'] = obter_estatisticas_historicas(file_path)
    return cache['historical_data']

def get_odds_cached():
    current_time = time.time()
    # 300 seconds = 5 minutes TTL
    if cache['odds_data'] is None or (current_time - cache['odds_last_fetch'] > 300):
        cache['odds_data'] = obter_proximas_partidas()
        cache['odds_last_fetch'] = current_time
    return cache['odds_data']

@app.route('/', methods=['GET', 'POST'])
def index():
    dados_historicos = get_historical_data_cached('results.csv')

    # Extract unique team names for the select boxes
    times = pd.concat([dados_historicos['time1'], dados_historicos['time2']]).unique().tolist()
    times.sort()

    # Default values
    banca = 10000.0
    time_casa = times[0] if times else ''
    time_visitante = times[1] if len(times) > 1 else ''
    odds_casa = 2.0
    odds_visitante = 2.0

    resultado_simulacao = None
    erro = None

    if request.method == 'POST':
        try:
            banca = float(request.form.get('banca', 10000.0))
            time_casa = request.form.get('time_casa')
            time_visitante = request.form.get('time_visitante')
            odds_casa = float(request.form.get('odds_casa', 2.0))
            odds_visitante = float(request.form.get('odds_visitante', 2.0))

            if time_casa == time_visitante:
                erro = "Por favor, selecione times diferentes."
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
                    erro = "Sem dados históricos para este confronto."
                else:
                    prob_casa_pct = df_previsao['prob_casa'].iloc[0] * 100
                    prob_visitante_pct = df_previsao['prob_visitante'].iloc[0] * 100
                    prob_empate_pct = df_previsao['prob_empate'].iloc[0] * 100

                    aposta_sugerida = df_previsao['aposta_sugerida'].iloc[0]
                    fracao_kelly = df_previsao['fracao_kelly'].iloc[0]
                    stake = banca * fracao_kelly if fracao_kelly > 0 else 0

                    resultado_simulacao = {
                        'vencedor': vencedor,
                        'prob_casa_pct': prob_casa_pct,
                        'prob_visitante_pct': prob_visitante_pct,
                        'prob_empate_pct': prob_empate_pct,
                        'aposta_sugerida': aposta_sugerida,
                        'fracao_kelly': fracao_kelly,
                        'stake': stake,
                        'time_casa': time_casa,
                        'time_visitante': time_visitante
                    }
        except Exception as e:
            erro = f"Erro ao processar simulação: {str(e)}"

    # Get upcoming matches and odds
    proximos_jogos = get_odds_cached()

    tabela_proximos_jogos = []
    if not proximos_jogos.empty:
        df_previsoes_finais = prever_vencedores(dados_historicos, proximos_jogos)

        df_exibicao = df_previsoes_finais.copy()
        df_exibicao['prob_casa'] = (df_exibicao['prob_casa'] * 100).apply(lambda x: f"{x:.1f}%")
        df_exibicao['prob_visitante'] = (df_exibicao['prob_visitante'] * 100).apply(lambda x: f"{x:.1f}%")
        df_exibicao['prob_empate'] = (df_exibicao['prob_empate'] * 100).apply(lambda x: f"{x:.1f}%")

        df_exibicao = df_exibicao.drop(columns=['fracao_kelly'])

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

        # Convert to list of dicts for template
        tabela_proximos_jogos = df_exibicao.to_dict('records')

    return render_template('index.html',
                           times=times,
                           banca=banca,
                           time_casa=time_casa,
                           time_visitante=time_visitante,
                           odds_casa=odds_casa,
                           odds_visitante=odds_visitante,
                           resultado_simulacao=resultado_simulacao,
                           erro=erro,
                           tabela_proximos_jogos=tabela_proximos_jogos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
