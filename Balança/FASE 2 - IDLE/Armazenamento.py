import os
import serial
import time
import datetime
from pathlib import Path

# Configurações
diretorio_do_script = Path(__file__).parent
DIRETORIO_DADOS = diretorio_do_script / "dados"
os.makedirs(DIRETORIO_DADOS, exist_ok=True)

# Gerar nome do arquivo
now = datetime.datetime.now()
nome_arquivo = now.strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
caminho_completo = os.path.join(DIRETORIO_DADOS, nome_arquivo)

beginMarker = "<"
endMarker = ">"

def salvar_dados(tipo, dados):
    """Salva os dados formatados no arquivo"""
    with open(caminho_completo, "a") as f:
        if tipo == "BALANCA":
            f.write(f"{dados}\n")
            #f.write(now.strtime("%d-%m-%Y_%H-%M-%S"))
        elif tipo == "MEDIA":
            f.write(f"MEDIA;{dados}\n")
            #f.write(now.strtime("%d-%m-%Y_%H-%M-%S"))
        elif tipo == "LEITURA":
            f.write(f"LEITURA;{dados}\n")
            #f.write(now.strtime("%d-%m-%Y_%H-%M-%S"))

def processar_mensagem(msg):
    """Processa mensagens completas do Arduino"""
    if msg.startswith("<BALANCA "):
        salvar_dados("BALANCA", msg[9:-1].replace(">", ""))
    elif msg.startswith("<MEDIA; "):
        salvar_dados("MEDIA", msg[8:-1].replace(">", ""))
    elif msg.startswith("<LEITURA; "):
        salvar_dados("LEITURA", msg[10:-1].replace(">", ""))

try:
    arduino = serial.Serial(port="COM6", baudrate=57600, timeout=1)
    buffer = ""
    print(f"Salvando dados em: {caminho_completo}")
    
    while True:
        if arduino.in_waiting > 0:
            # Ler todos os bytes disponíveis
            data = arduino.read(arduino.in_waiting).decode(errors='ignore')
            buffer += data
            
            # Processar mensagens completas
            while '<' in buffer and '>' in buffer:
                start = buffer.index('<')
                end = buffer.index('>', start) + 1
                
                if end > start:
                    msg = buffer[start:end]
                    processar_mensagem(msg)
                    buffer = buffer[end:]
                else:
                    break
                    
        time.sleep(0.01)

except Exception as e:
    print(f"Erro: {e}")
finally:
    if 'arduino' in locals():
        arduino.close()
    
