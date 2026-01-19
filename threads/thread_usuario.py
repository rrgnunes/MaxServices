import os
import sys
from datetime import datetime, timedelta
from fdb import Cursor
# import socket
# import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from funcoes.funcoes import (
    updatefb,
    print_log,
    obter_dados_ini,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    verifica_dll_firebird,
    inicializa_conexao_firebird
    )

# HOST = '0.0.0.0'
# PORT = 50002

def marcar_logado(codigo_empresa, codigo_usuario):
    print_log(f"Marcando usuario {codigo_usuario} da empresa {codigo_empresa} como logado.", nome_script)
    sql = "UPDATE USUARIOS SET LOGADO = 1 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

def marcar_deslogado(codigo_empresa, codigo_usuario):
    print_log(f"Marcando usuario {codigo_usuario} da empresa {codigo_empresa} como deslogado.", nome_script)
    sql = "UPDATE USUARIOS SET LOGADO = 0 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

# def handle_client(conn, addr):
#     codigo_empresa = None
#     codigo_usuario = None
#     try:
#         print_log(f"Conexão de {addr}")
#         data = conn.recv(1024).decode().strip()
#         partes = data.split(';')

#         if len(partes) == 3 and partes[0] == 'LOGIN':
#             codigo_empresa = int(partes[1])
#             codigo_usuario = int(partes[2])

#             marcar_logado(codigo_empresa, codigo_usuario)
#             print_log(f"Usuário {codigo_usuario} da empresa {codigo_empresa} logado.")

#             while True:
#                 msg = conn.recv(1024)
#                 if not msg:
#                     break

#     except Exception as e:
#         print_log(f"Erro cliente {addr}: {e}")

#     finally:
#         if codigo_empresa and codigo_usuario:
#             print_log(f"Desconectado: Usuário {codigo_usuario} da empresa {codigo_empresa}")
#             marcar_deslogado(codigo_empresa, codigo_usuario)
#         conn.close()

# def start_server():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
#         server.bind((HOST, PORT))
#         server.listen()
#         print_log(f"Servidor Socket rodando na porta {PORT}")

#         while True:
#             conn, addr = server.accept()
#             threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def verifica_usuarios():

    caminho_sistema = params.SCRIPT_PATH.lower().replace('server', '')
    caminho_banco_ini = os.path.join(caminho_sistema, 'banco.ini')
    dados_ini = obter_dados_ini(caminho_banco_ini)

    params.PATHDLL = verifica_dll_firebird()
    params.DATABASEFB = dados_ini['caminho_banco']

    inicializa_conexao_firebird()

    sql_select = f"SELECT CODIGO, FK_EMPRESA, LOGADO, ULT_EXEC_USUARIO FROM USUARIOS WHERE ATIVO = 'S'"
    cursor = None
    try:
        print_log(f"Consultando usuarios do sistema...", nome_script)
        cursor: Cursor = params.FIREBIRD_CONNECTION.cursor()
        cursor.execute(sql_select)
        usuarios = cursor.fetchall()
        hora_atual = datetime.now()

        for usuario in usuarios:
            
            if usuario[2] == 0:
                continue
            
            if not usuario[3]:
                marcar_deslogado(usuario[1], usuario[0])
                continue

            if (hora_atual - usuario[3]) > timedelta(seconds=20):
                marcar_deslogado(usuario[1], usuario[0])

    except Exception as e:
        print_log(f"Não foi possível verificar usuarios -> motivo: {e}")
        
    finally:
        print_log("Consulta de usuarios finalizada.", nome_script)
        if cursor:
            cursor.close()


if __name__ == "__main__":
    # host = get_local_ip()  # Obtém o IP local da máquina
    # if host == '192.168.10.115':
    #     parametros.HOSTFB = 'MAXSUPORT-09'

    # parametros.DATABASEFB = 'C:\\MaxSuport\\Dados\\Dados.fdb'
    # parametros.HOSTFB = host
    # parametros.PATHDLL = verifica_dll_firebird()
    # inicializa_conexao_firebird()
    # start_server()

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            verifica_usuarios()
        except Exception as e:
            print_log(f"Erro ao tentar iniciar verificação -> motivo: {e}", nome_script)
        finally:
            remover_bloqueio(nome_script)