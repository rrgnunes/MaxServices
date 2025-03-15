import re
import pathlib
import os
import configparser
import socket
import fdb
import time
from enum import Enum

class Send_Cmd(Enum):
    OK = b"#ok"
    ALIVE = "#live?"
    ALWAYS_ON = b"#alwayslive"

class Receive_Cmd(Enum):
    RESPONSE_OK = '#tc'
    RESPONSE_ALIVE = '#alive'
    RESPONSE_ALWAYS_ON = "#alwayslive_ok"
    RESPONSE_ALWAYS_VERSAO = "#bpg2e"

def split_string(string, max_length, price_top = False):
    words = string.split()
    lines = []
    current_line = ""

    if price_top:
        title = '*** ' + words[-1].strip() + ' ***' 
        lines.append(title.center(max_length))
        # lines.append('*** ' + words[-1].strip() + ' ***')
        words = words[:-1]

    for word in words:
        if len(current_line) + len(word) <= max_length:
            current_line += word + " "
        else:
            lines.append(current_line.strip().ljust(max_length))
            current_line = word + " "

    if not price_top:
        lines.append('*** ' + current_line.strip() + ' ***')
    else:
        lines.append(current_line.strip())

    return ' ' + ''.join(lines)

def check_terminal_alive(client):
    print('Check online status')
    comando = Send_Cmd.ALIVE.value.encode('ascii')
    client.send(comando)
    time.sleep(0.5)
    resposta = client.recv(255)
    resposta = resposta.decode('ascii')
    print('OK')
    return


def set_always_on(client):
    resposta = None  # Variável para guardar a resposta
    print('Set always mode')
    comando = Send_Cmd.ALWAYS_ON.value  # Transforma a string em bytes
    client.send(comando)  # Envia o comando para o equipamento
    time.sleep(0.5)  # Tempo para garantir resposta do equipamento
    dados = client.recv(255)  # Faz a leitura da resposta do Busca Preço
    resposta = dados.decode('ascii')  # Converte os bytes para texto.
    if Receive_Cmd.RESPONSE_ALWAYS_ON.value in resposta:
        print('OK')
    else:
        print(f'Retorno inválido {resposta}')


def await_terminal_query(client):
    data = read_ini()
    server = "localhost"
    port = data['porta']
    path = data['path']
    user = "gfilmaster"
    password = "b32@m451"
    connected = False
    # Criando as strings de conexão com a porta
    dsn = f"{server}/{port}:{path}"
    fdb.load_api(f'C:/Program Files/Firebird/Firebird_4_0/fbclient.dll')

    while not connected:
        try:
            # Conexões
            con = fdb.connect(dsn=dsn, user=user, password=password)
            cursor = con.cursor()
            connected = True
        except Exception as e:
            print(f'não foi possivel conectar ao banco: {e}')

    while True:
        print('Awaiting for query')
        # dados = client.recv(255).decode('ascii')
        dados = client.recv(255).decode("utf8")
        # time.sleep(0.5)
        print(f'Consultando: {dados}')
        if terminal_input_valid(dados):
            return_query(client, dados, cursor)
        else:
            print('Invalid terminal return')

def return_query(client,dados, cursor):
    codigo_barra = dados[1:14]

    sql = f"""select
                p.codigobarras , p.cbarra, p.descricao, pps.preco
            from precos_prod_serv pps
                left outer join tabs_precos_prod_serv tpps
                    on tpps.codigo = pps.tabela
                left outer join produtos p
                    on p.cod_alfa = pps.produto
            where tpps.tabpadrao = 'S' and pps.tipoproduto = 'P'
             and (codigobarras = '{codigo_barra}' or cbarra = '{codigo_barra}')"""
    print(sql)
    cursor.execute(sql)
    # Obtém os nomes das colunas
    colunas = [coluna[0] for coluna in cursor.description]

    # Constrói uma lista de dicionários, onde cada dicionário representa uma linha
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    if len(resultados_em_dicionario ) > 0:
        produto = resultados_em_dicionario[0]
        print(produto)
    else:
        produto = None

    print(produto)        
    
    # Define os parâmetros que serão enviados na função
    if produto is None:
        Linha1 = 'Produto nao encontrado'
        Linha1 = split_string(Linha1, 20, False)
    else:
        Linha1 = produto['DESCRICAO'][:40] + " " + f"R${produto['PRECO']:,.2f}"
        Linha1 = split_string(Linha1, 20, True)
    str = Linha1 
    print(str)
    comando = str.encode("cp1255")  # Transforma a string em bytes
    client.send(comando)  # Envia o comando para o equipamento
    print(f'Resposta consulta retornada: {str}')
    # time.sleep(5)
    return

def terminal_input_valid(string):
    pattern = r'^#(\d)'
    match = re.match(pattern, string)
    if match:
        return True
    return False
    
def read_ini():
    path = pathlib.Path(__file__).parent.parent
    path_bd = os.path.join(path, 'Dados', 'Infolivre.fdb')
    ini_path = os.path.join(path, 'Conexao.ini')
    print(path)
    print(ini_path)
    try:
        config = configparser.ConfigParser()
        config.read(ini_path)
        porta = config.get('Firebird', 'Porta')
    except Exception as e:
        print(f'Nao foi possivel ler arquivo .ini: {e}, {ini_path}')

    data = {"porta": f'{porta}', "path": f'{path_bd}'}

    return data

def log_error(message):
    with open("C:\\connection_error.log", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def cleanup():
    if client:
        client.close()
    if server:
        server.close()
    print("MaxSuport_BuscaPreco - Socket server closed.")

try:
    # Cria um socket do servidor
    ip_server = socket.get
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_server, 6500))
    server.listen()
    print(f'Listening: {ip_server}:6500')

    # Aceita uma conexão de um cliente
    client, _ = server.accept()

    # Envia um comando para o cliente
    client.send(Send_Cmd.OK.value)
    time.sleep(0.5)

    while not stop_requested:
        try:
            # Recebe uma resposta do cliente
            response = client.recv(255)
            response = response.decode("ascii")
            log_error(response)

            if '|' in response:
                print(response)
                cmd = response.split('|')[0]
                if Receive_Cmd(cmd[:6]) == Receive_Cmd.RESPONSE_ALWAYS_VERSAO:
                    print('Versão g2 E')
                    check_terminal_alive(client)
                    set_always_on(client)
                    await_terminal_query(client)
                elif Receive_Cmd(cmd[:3]) == Receive_Cmd.RESPONSE_OK:
                    print('Client connected')
                    check_terminal_alive(client)
                    set_always_on(client)
                    await_terminal_query(client)
                    print('fim')
        except Exception as e:
            log_error(f"Erro no loop principal: {e.__class__.__name__} - {e}")
            break

except Exception as e:
    log_error(f"Erro ao iniciar o servidor: {e.__class__.__name__} - {e}")
finally:
    cleanup()