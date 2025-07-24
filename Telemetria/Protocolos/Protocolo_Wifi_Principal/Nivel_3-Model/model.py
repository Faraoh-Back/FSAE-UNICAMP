# Nivel_3-TratamentoDados/model.py
import pandas as pd
from supabase import create_client, Client

class TelemetryModel:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.tabela_dados = "telemetria-sensores"
        self.tabela_controle = "controle_telemetria"

    def get_telemetry_status(self) -> bool:
        """Verifica no Supabase se a coleta está ativa."""
        try:
            response = self.supabase.table(self.tabela_controle).select('coleta_ativa').eq('id', 1).single().execute()
            return response.data.get('coleta_ativa', False)
        except Exception:
            return False

    def set_telemetry_status(self, new_status: bool) -> bool:
        """Define o estado da coleta (ativa/inativa) no Supabase."""
        try:
            self.supabase.table(self.tabela_controle).update({'coleta_ativa': new_status}).eq('id', 1).execute()
            return True
        except Exception as e:
            print(f"Erro ao definir o estado da telemetria: {e}")
            return False

    def get_live_data(self, limit: int = 100) -> list:
        """Busca os dados mais recentes do Supabase para os gráficos."""
        try:
            response = self.supabase.table(self.tabela_dados).select("*").order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar dados ao vivo: {e}")
            return []

    def get_statistics(self) -> dict:
        """Busca todos os dados e calcula as estatísticas."""
        try:
            response = self.supabase.table(self.tabela_dados).select("*").execute()
            if not response.data:
                return {}

            df = pd.DataFrame(response.data)
            df = df.drop(columns=['id', 'created_at'], errors='ignore')
            
            stats = df.describe().to_dict()
            
            resultado = {
                col: {
                    'media': round(data.get('mean', 0), 2),
                    'min': data.get('min', 0),
                    'max': data.get('max', 0),
                    'desvio_padrao': round(data.get('std', 0), 2)
                } for col, data in stats.items()
            }
            return resultado
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            return {}