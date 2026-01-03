import os
import sys
import socket
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes import updatefb, print_log, get_local_ip, inicializa_conexao_firebird, verifica_dll_firebird

HOST = '0.0.0.0'
PORT = 50002

def marcar_logado(codigo_empresa, codigo_usuario):
    sql = "UPDATE USUARIOS SET LOGADO = 1 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

def marcar_deslogado(codigo_empresa, codigo_usuario):
    sql = "UPDATE USUARIOS SET LOGADO = 0 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

def handle_client(conn, addr):
    codigo_empresa = None
    codigo_usuario = None
    try:
        print_log(f"Conexão de {addr}")
        data = conn.recv(1024).decode().strip()
        partes = data.split(';')

        if len(partes) == 3 and partes[0] == 'LOGIN':
            codigo_empresa = int(partes[1])
            codigo_usuario = int(partes[2])

            marcar_logado(codigo_empresa, codigo_usuario)
            print_log(f"Usuário {codigo_usuario} da empresa {codigo_empresa} logado.")

            while True:
                msg = conn.recv(1024)
                if not msg:
                    break

    except Exception as e:
        print_log(f"Erro cliente {addr}: {e}")

    finally:
        if codigo_empresa and codigo_usuario:
            print_log(f"Desconectado: Usuário {codigo_usuario} da empresa {codigo_empresa}")
            marcar_deslogado(codigo_empresa, codigo_usuario)
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print_log(f"Servidor Socket rodando na porta {PORT}")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    host = get_local_ip()  # Obtém o IP local da máquina
    if host == '192.168.10.115':
        parametros.HOSTFB = 'MAXSUPORT-09'

    parametros.DATABASEFB = 'C:\\MaxSuport\\Dados\\Dados.fdb'
    parametros.HOSTFB = host
    parametros.PATHDLL = verifica_dll_firebird()
    inicializa_conexao_firebird()
    start_server()
