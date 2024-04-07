from funcoes import *
import socket


def handle_client_connection(client_socket):
    """
    Função para tratar a conexão com cada cliente em uma thread separada.
    """
    try:

        dados = ''
        while True:
            chunk = client_socket.recv(1).decode('utf-8')  # Lê byte a byte
            if chunk == '\n' or chunk == '':  # Verifica o delimitador de nova linha ou string vazia
                break
            dados += chunk

        comando_sql = dados

        resultado = consultar_sqlite(comando_sql)
        
        resposta = json.dumps(resultado)  + '\n'  # Converte o resultado para JSON
        client_socket.sendall(resposta.encode())  # Envia a resposta JSON de volta ao cliente
    except Exception as e:
        print_log(f"Erro ao tratar a conexão do cliente: {e}")

def servidor_socket():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 50001))
            s.listen()
            print_log(f"Servidor escutando em '127.0.0.1':'50001'")
            
            while True:
                conn, addr = s.accept()  # Aceita uma nova conexão
                print_log(f"Conectado por {addr}")
                client_thread = threading.Thread(target=handle_client_connection, args=(conn,))
                client_thread.start()  # Inicia a thread para tratar a conexão
    except Exception as e:
        print_log(f"Erro no servidor: {e}")                    

servidor_socket()