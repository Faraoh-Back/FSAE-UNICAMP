import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial.tools.list_ports

# --- Configurações ---
PASTA_ARMAZENAMENTO = os.path.join(os.path.dirname(__file__), '..', 'Nivel_4_Armazenamento')
ARQUIVO_DADOS_BRUTOS = os.path.join(PASTA_ARMAZENAMENTO, 'DADOS_BRUTOS.csv')
ARQUIVO_ESTATISTICAS = os.path.join(PASTA_ARMAZENAMENTO, 'ESTATISTICAS.json')
ARQUIVO_PARAMETROS = os.path.join(PASTA_ARMAZENAMENTO, 'PARAMETROS.json')

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teste de Rádios LoRa")
        self.geometry("1200x800")

        self.rodando_teste = False
        self._create_widgets()
        self.update_gui()

    def _create_widgets(self):
        # Frame de controle
        control_frame = ttk.LabelFrame(self, text="Parâmetros do Teste", padding="10")
        control_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Seleção de Porta Serial
        ttk.Label(control_frame, text="Porta Serial:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.serial_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.serial_var = tk.StringVar(value=self.serial_ports[0] if self.serial_ports else "")
        self.serial_menu = ttk.Combobox(control_frame, textvariable=self.serial_var, values=self.serial_ports, width=15)
        self.serial_menu.grid(row=0, column=1, padx=5, pady=5)

        # Quantidade de Medidas
        ttk.Label(control_frame, text="Qtde. de Medidas:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.qtde_var = tk.StringVar(value="100")
        self.qtde_entry = ttk.Entry(control_frame, textvariable=self.qtde_var, width=18)
        self.qtde_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botão Iniciar/Parar
        self.start_stop_button = ttk.Button(control_frame, text="Iniciar Teste", command=self.toggle_test)
        self.start_stop_button.grid(row=0, column=2, rowspan=2, padx=20, pady=5, sticky="ns")

        # Frame de Estatísticas
        stats_frame = ttk.LabelFrame(self, text="Estatísticas em Tempo Real", padding="10")
        stats_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        self.stats_labels = {}
        headers = ["", "RSSI Máxima", "RSSI Mínima", "RSSI Média", "Desvio Padrão"]
        for col, header in enumerate(headers):
            ttk.Label(stats_frame, text=header, font=('Helvetica', 10, 'bold')).grid(row=0, column=col, padx=5)

        rows = ["Downlink", "Uplink"]
        for row, name in enumerate(rows, 1):
             ttk.Label(stats_frame, text=name, font=('Helvetica', 10, 'bold')).grid(row=row, column=0, sticky="w", padx=5)
             for col in range(1, 5):
                var = tk.StringVar(value="--")
                self.stats_labels[f"{name}_{col}"] = var
                ttk.Label(stats_frame, textvariable=var, width=15).grid(row=row, column=col)

        ttk.Label(stats_frame, text="PSR Geral:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, pady=10, sticky="w", padx=5)
        self.psr_var = tk.StringVar(value="--")
        ttk.Label(stats_frame, textvariable=self.psr_var).grid(row=3, column=1, pady=10)

        # Frame do Gráfico
        graph_frame = ttk.Frame(self)
        graph_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_test(self):
        self.rodando_teste = not self.rodando_teste
        if self.rodando_teste:
            self.start_stop_button.config(text="Parar Teste")
            config = {
                'rodando': True,
                'porta_serial': self.serial_var.get(),
                'baud_rate': 115200, # Fixo baseado no seu firmware
                'qtde_medidas': int(self.qtde_var.get())
            }
        else:
            self.start_stop_button.config(text="Iniciar Teste")
            config = {'rodando': False}
        
        with open(ARQUIVO_PARAMETROS, 'w') as f:
            json.dump(config, f, indent=4)

    def update_gui(self):
        if self.rodando_teste:
            self.update_stats()
            self.update_graph()

        # Re-agenda a atualização
        self.after(1000, self.update_gui)

    def update_stats(self):
        try:
            with open(ARQUIVO_ESTATISTICAS, 'r') as f:
                stats = json.load(f)

            # Downlink
            self.stats_labels["Downlink_1"].set(f"{stats['downlink']['max_rssi']:.2f} dBm")
            self.stats_labels["Downlink_2"].set(f"{stats['downlink']['min_rssi']:.2f} dBm")
            self.stats_labels["Downlink_3"].set(f"{stats['downlink']['media_rssi']:.2f} dBm")
            self.stats_labels["Downlink_4"].set(f"{stats['downlink']['desvio_padrao_rssi']:.2f}")

            # Uplink
            self.stats_labels["Uplink_1"].set(f"{stats['uplink']['max_rssi']:.2f} dBm")
            self.stats_labels["Uplink_2"].set(f"{stats['uplink']['min_rssi']:.2f} dBm")
            self.stats_labels["Uplink_3"].set(f"{stats['uplink']['media_rssi']:.2f} dBm")
            self.stats_labels["Uplink_4"].set(f"{stats['uplink']['desvio_padrao_rssi']:.2f}")
            
            self.psr_var.set(f"{stats['psr_geral']:.2f} % ({stats['total_pacotes']} pacotes)")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def update_graph(self):
        try:
            df = pd.read_csv(ARQUIVO_DADOS_BRUTOS, sep=';')
            if df.empty:
                return

            self.ax.clear()
            self.ax.plot(df.index, df['rssi_downlink'], label='RSSI Downlink (dBm)', alpha=0.7)
            self.ax.plot(df.index, df['rssi_uplink'], label='RSSI Uplink (dBm)', alpha=0.7)

            # Média móvel
            df['rssi_dl_rolling'] = df['rssi_downlink'].rolling(window=10).mean()
            df['rssi_ul_rolling'] = df['rssi_uplink'].rolling(window=10).mean()
            self.ax.plot(df.index, df['rssi_dl_rolling'], label='Média Móvel DL', color='blue', linewidth=2)
            self.ax.plot(df.index, df['rssi_ul_rolling'], label='Média Móvel UL', color='red', linewidth=2)
            
            self.ax.set_xlabel("Número da Medida")
            self.ax.set_ylabel("RSSI (dBm)")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
            
        except (FileNotFoundError, pd.errors.EmptyDataError):
            pass

if __name__ == "__main__":
    if not os.path.exists(PASTA_ARMAZENAMENTO):
        os.makedirs(PASTA_ARMAZENAMENTO)
    app = AppGUI()
    app.mainloop()