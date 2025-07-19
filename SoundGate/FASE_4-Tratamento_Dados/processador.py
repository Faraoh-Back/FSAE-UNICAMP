import pandas as pd
import json
import os
import sys

PASTA_ARMAZENAMENTO = sys.argv[1]
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'dados_brutos.csv')
ARQUIVO_METRICAS = os.path.join(PASTA_ARMAZENAMENTO, 'metricas.json')

def analisar_dados():
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS)
        
        # --- INÍCIO DA CORREÇÃO ---
        # Se houver dados, ignora a primeira linha (Volta 0 ou o ponto de partida)
        # .iloc[1:] seleciona todas as linhas a partir da segunda (índice 1)
        if not df.empty and len(df) > 0:
            df = df.iloc[1:].reset_index(drop=True)
        # --- FIM DA CORREÇÃO ---

        # Se após remover a primeira linha não sobrar nada, encerra.
        if df.empty:
            # Limpa o arquivo de métricas para não mostrar dados antigos
            if os.path.exists(ARQUIVO_METRICAS):
                os.remove(ARQUIVO_METRICAS)
            return

        # Pega os nomes das colunas diretamente do arquivo
        col_volta, col_dist, col_tempo_volta, col_tempo_total = df.columns

        # Limpa as colunas, removendo as unidades
        df[col_dist] = pd.to_numeric(df[col_dist].str.replace(' cm', '', regex=False), errors='coerce')
        df[col_tempo_volta] = pd.to_numeric(df[col_tempo_volta].str.replace(' seg', '', regex=False), errors='coerce')
        df[col_tempo_total] = pd.to_numeric(df[col_tempo_total].str.replace(' seg', '', regex=False), errors='coerce')
        
        df.dropna(subset=[col_tempo_volta], inplace=True)

        # Agora os cálculos serão feitos apenas com as voltas reais
        tempos_de_volta = df[col_tempo_volta].tolist()
        melhor_volta = df[col_tempo_volta].min()
        pior_volta = df[col_tempo_volta].max()
        media_voltas = df[col_tempo_volta].mean()
        desvio_padrao = df[col_tempo_volta].std()
        # O total de voltas "reais" é o número de linhas do novo dataframe
        total_voltas = len(df)
        
        if pd.isna(desvio_padrao):
            desvio_padrao = 0

        metricas = {
            'total_voltas': total_voltas,
            'melhor_volta': round(melhor_volta, 3),
            'pior_volta': round(pior_volta, 3),
            'media_voltas': round(media_voltas, 3),
            'desvio_padrao': round(desvio_padrao, 3),
            'tempos_de_volta': tempos_de_volta
        }
        
        with open(ARQUIVO_METRICAS, 'w') as f:
            json.dump(metricas, f, indent=4)
        
        print(f"Métricas calculadas (ignorando a 1ª linha) e salvas em {ARQUIVO_METRICAS}")

    except FileNotFoundError:
        print(f"AVISO: Arquivo de dados brutos não encontrado.")
    except Exception as e:
        print(f"Um erro inesperado ocorreu no processador: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho para a pasta de armazenamento como argumento.")
    else:
        analisar_dados()