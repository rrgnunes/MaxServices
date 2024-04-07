from funcoes import *
import socket
import threading

# thread do alerta bloqueio
class threadservidorsocket(threading.Thread):
    def __init__(self, host='127.0.0.1', port=50001):
        super().__init__()
        self.event = threading.Event()
        self.host = host  # Endereço IP onde o servidor vai escutar
        self.port = port  # Porta TCP onde o servidor vai escutar

    def run(self):
        self.servidor_socket()

    def handle_client_connection(self,client_socket):
        """
        Função para tratar a conexão com cada cliente em uma thread separada.
        """
        try:
            with client_socket as conn:
                while True:
                    dados = conn.recv(1024)
                    if not dados:
                        break  # Encerra o loop se não receber dados
                    comando_sql = dados.decode('utf-8')
                    resultado = consultar_sqlite(comando_sql)
                    
                    resposta = json.dumps(resultado)  # Converte o resultado para JSON
                    conn.sendall(resposta.encode())  # Envia a resposta JSON de volta ao cliente
        except Exception as e:
            print_log(f"Erro ao tratar a conexão do cliente: {e}")
        finally:
            conn.close()

    def servidor_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                print_log(f"Servidor escutando em {self.host}:{self.port}")
                
                while True:
                    conn, addr = s.accept()  # Aceita uma nova conexão
                    print_log(f"Conectado por {addr}")
                    client_thread = threading.Thread(target=self.handle_client_connection, args=(conn,))
                    client_thread.start()  # Inicia a thread para tratar a conexão
        except Exception as e:
            print_log(f"Erro no servidor: {e}")      
