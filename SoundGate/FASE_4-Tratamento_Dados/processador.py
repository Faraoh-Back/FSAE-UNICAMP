import pandas as pd
import json
import os
import sys

# O caminho para a pasta de armazenamento é passado como argumento
PASTA_ARMAZENAMENTO = sys.argv[1]
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'dados_brutos.csv')
ARQUIVO_METRICAS = os.path.join(PASTA_ARMAZENAMENTO, 'metricas.json')

def analisar_dados():
    """Lê o CSV de dados brutos, calcula as métricas e salva em JSON."""
    try:
        df = pd.read_csv(ARQUIVO_DADOS_BRUTOS)
        if df.empty:
            print("AVISO: Arquivo de dados brutos está vazio.")
            return

        # Garante que a coluna 'Tempo de Volta' é numérica
        df['Tempo de Volta'] = pd.to_numeric(df['Tempo de Volta'], errors='coerce')
        df.dropna(subset=['Tempo de Volta'], inplace=True)

        # Calcula as métricas
        tempos_de_volta = df['Tempo de Volta'].tolist()
        melhor_volta = df['Tempo de Volta'].min()
        pior_volta = df['Tempo de Volta'].max()
        media_voltas = df['Tempo de Volta'].mean()
        desvio_padrao = df['Tempo de Volta'].std()
        total_voltas = len(df)
        
        # O desvio padrão pode ser NaN se houver apenas uma volta
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
        
        # Salva as métricas em um arquivo JSON
        with open(ARQUIVO_METRICAS, 'w') as f:
            json.dump(metricas, f, indent=4)
        
        print(f"Métricas calculadas e salvas em {ARQUIVO_METRICAS}")

    except FileNotFoundError:
        print(f"ERRO: Arquivo de dados brutos não encontrado em {ARQUIVO_DADOS_BRUTOS}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Forneça o caminho para a pasta de armazenamento como argumento.")
    else:
        analisar_dados()