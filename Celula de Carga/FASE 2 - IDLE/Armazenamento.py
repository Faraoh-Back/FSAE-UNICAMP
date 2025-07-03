import os
import serial
import time
import datetime

# Configurações
DIRETORIO_DADOS = r"C:\Users\Otaldo\OneDrive\Organizar Pessoal OneDrive\Documentos\FSAE_Metais\FASE 3 - Armazenamento"
PORTA_SERIAL = "COM3"
BAUDRATE = 57600  # Ajustado para coincidir com o Arduino

# Criar diretório se não existir
os.makedirs(DIRETORIO_DADOS, exist_ok=True)

# Gerar nome do arquivo com timestamp
now = datetime.datetime.now()
nome_arquivo = now.strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
caminho_completo = os.path.join(DIRETORIO_DADOS, nome_arquivo)

print(f"Configurações:")
print(f"  Porta: {PORTA_SERIAL}")
print(f"  Baudrate: {BAUDRATE}")
print(f"  Arquivo: {caminho_completo}")
print(f"  Formato esperado: <dado1;dado2>")
print("-" * 50)

try:
    # Conectar ao Arduino
    arduino = serial.Serial(port=PORTA_SERIAL, baudrate=BAUDRATE, timeout=1)
    print(f"Conectado ao Arduino na porta {PORTA_SERIAL}")
    print("Aguardando dados...")
    print("Pressione Ctrl+C para encerrar...")
    
    # Aguardar um pouco para o Arduino inicializar
    time.sleep(2)
    
    contador_dados = 0
    
    with open(caminho_completo, "w", encoding='utf-8') as arquivo:
        
        while True:
            if arduino.in_waiting > 0:
                try:
                    linha = arduino.readline().decode('utf-8', errors='ignore').strip()
                    
                    # Verificar se a linha está no formato esperado <dado1;dado2>
                    if linha.startswith('<') and linha.endswith('>') and ';' in linha:
                        # Extrai os valores entre os marcadores < >
                        valores = linha[1:-1]  # Remove < e >
                        
                        # Validar se contém exatamente um ponto e vírgula
                        if valores.count(';') == 1:
                            # Obtém hora atual formatada
                            hora = datetime.datetime.now().strftime("%H:%M:%S")
                            
                            # Escreve no arquivo: dado1;dado2[hora]
                            linha_arquivo = f"{valores}[{hora}]\n"
                            arquivo.write(linha_arquivo)
                            arquivo.flush()  # Garante escrita imediata
                            
                            contador_dados += 1
                            
                            # Mostrar dados na tela (opcional)
                            dados = valores.split(';')
                            print(f"[{hora}] Dado1: {dados[0]:<8} | Dado2: {dados[1]:<8} | Total: {contador_dados}")
                    
                    # Mostrar outras mensagens do Arduino (como inicialização)
                    elif linha and not linha.startswith('<'):
                        print(f"Arduino: {linha}")
                        
                except UnicodeDecodeError:
                    print("Erro de decodificação - linha ignorada")
                    continue
            
            time.sleep(0.01)  # Pequena pausa para não sobrecarregar o CPU
            
except KeyboardInterrupt:
    print(f"\n\nColeta encerrada pelo usuário")
    print(f"Total de dados coletados: {contador_dados}")
    
except serial.SerialException as e:
    print(f"Erro de comunicação serial: {e}")
    print("Verifique se:")
    print("  - O Arduino está conectado")
    print("  - A porta COM está correta")
    print("  - Nenhum outro programa está usando a porta")
    
except Exception as e:
    print(f"Erro inesperado: {e}")
    
finally:
    if 'arduino' in locals():
        arduino.close()
        print("Conexão serial fechada")
    print(f"Dados salvos em: {caminho_completo}")
    print("Programa finalizado.")
