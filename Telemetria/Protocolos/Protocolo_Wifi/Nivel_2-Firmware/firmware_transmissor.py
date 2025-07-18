# servidor_wifi.py
import http.server
import socketserver

PORT = 8000
DATA_FILE = 'telemetry_data.csv'

class TelemetryHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            try:
                # Abre o arquivo de dados e lê a última linha (a mais recente)
                with open(DATA_FILE, 'rb') as f:
                    try:  # Tenta ler as últimas linhas de forma eficiente
                        f.seek(-1024, 2)
                        last_line = f.readlines()[-1].decode('utf-8').strip()
                    except OSError:  # Caso o arquivo seja pequeno
                        f.seek(0)
                        lines = f.readlines()
                        last_line = lines[-1].decode('utf-8').strip() if lines else ""

                # Envia a resposta para o cliente (ESP8266)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(last_line.encode('utf-8'))

            except Exception as e:
                # Envia uma resposta de erro se algo der errado
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao ler o arquivo de dados: {e}".encode('utf-8'))
        else:
            # Resposta para qualquer outro caminho
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint nao encontrado. Use /data")

with socketserver.TCPServer(("", PORT), TelemetryHandler) as httpd:
    print(f"--- Servidor de Telemetria Iniciado na porta {PORT} ---")
    print(f"Aguardando conexoes do ESP8266 no IP 192.168.4.1:{PORT}/data")
    httpd.serve_forever()