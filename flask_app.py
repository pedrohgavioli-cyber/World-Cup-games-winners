from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import time
from data_prep import preparar_estatisticas_equipes
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
        cache['historical_data'] = preparar_estatisticas_equipes(file_path)
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
    times = list(dados_historicos['forcas_equipes'].keys())
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

                    xg_casa = df_previsao['xg_casa'].iloc[0]
                    xg_visitante = df_previsao['xg_visitante'].iloc[0]

                    aposta_sugerida = df_previsao['aposta_sugerida'].iloc[0]
                    fracao_kelly = df_previsao['fracao_kelly'].iloc[0]
                    stake = banca * fracao_kelly if fracao_kelly > 0 else 0

                    resultado_simulacao = {
                        'vencedor': vencedor,
                        'prob_casa_pct': prob_casa_pct,
                        'prob_visitante_pct': prob_visitante_pct,
                        'prob_empate_pct': prob_empate_pct,
                        'xg_casa': xg_casa,
                        'xg_visitante': xg_visitante,
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

    return render_template('index.html',
                           times=times,
                           banca=banca,
                           time_casa=time_casa,
                           time_visitante=time_visitante,
                           odds_casa=odds_casa,
                           odds_visitante=odds_visitante,
                           resultado_simulacao=resultado_simulacao,
                           erro=erro,
                           proximos_jogos=proximos_jogos.to_dict('records'))

@app.route('/predict_match', methods=['POST'])
def predict_match():
    """
    Endpoint para prever uma única partida sob demanda.
    Recebe os dados da partida via JSON e retorna a previsão.
    """
    try:
        match_data = request.json
        if not match_data or 'jogo' not in match_data:
            return jsonify({'erro': 'Dados da partida ausentes.'}), 400

        dados_historicos = get_historical_data_cached('results.csv')

        # Cria um DataFrame para a partida selecionada
        partida_df = pd.DataFrame([match_data])

        # Executa a previsão para esta única partida
        previsao_df = prever_vencedores(dados_historicos, partida_df)

        if previsao_df.empty:
            return jsonify({'erro': 'Não foi possível gerar a previsão.'}), 500

        # Converte o resultado para um dicionário e prepara para JSON
        resultado = previsao_df.iloc[0].to_dict()

        # O campo 'placares_provaveis' já é uma string JSON, então precisamos decodificá-lo
        # para que o jsonify possa codificá-lo corretamente no objeto de resposta.
        if 'placares_provaveis' in resultado and isinstance(resultado['placares_provaveis'], str):
            resultado['placares_provaveis'] = json.loads(resultado['placares_provaveis'])

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'erro': f'Ocorreu um erro no servidor: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
