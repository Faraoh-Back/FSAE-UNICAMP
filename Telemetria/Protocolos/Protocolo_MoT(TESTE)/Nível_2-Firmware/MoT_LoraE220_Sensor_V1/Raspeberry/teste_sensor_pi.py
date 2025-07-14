import time
# ... (importe a sua classe E220TTL e configure o objeto e220ttl) ...

e220ttl = E220TTL()
e220ttl.begin()
e220ttl.configure_lora() # Garante que está nos mesmos parâmetros da base

print("Sensor de Teste Pronto. Ouvindo por 'PING'...")

while True:
  # Ouve por uma mensagem
  received_message, rssi = e220ttl.receiveMessageRSSI()
  if received_message:
    print(f"Mensagem recebida: {received_message.decode('utf-8', 'ignore')}")
    
    # Se receber "PING", responde com "PONG"
    if "PING" in received_message.decode('utf-8', 'ignore'):
      print("PING recebido! Enviando PONG para a Base (Endereco 1)...")
      # O endereço da base deve ser 1, conforme o .h da base
      e220ttl.sendMessage(1, 65, b"PONG do Pi!") 
  
  time.sleep(0.1)