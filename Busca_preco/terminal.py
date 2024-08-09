import re
import time
import pathlib
import os
import configparser
import fdb
from commands import Receive_Cmd, Send_Cmd
from rich import print
from util import split_string


def check_terminal_alive(client):
    # comando = "#live?"
    print('Check online status')
    comando = Send_Cmd.ALIVE.value.encode('ascii')
    client.send(comando)
    time.sleep(0.5)
    resposta = client.recv(255)
    resposta = resposta.decode('ascii')
    # print(resposta + '/n')
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
    # data = read_ini()
    # server = "localhost"
    # port = data['porta']
    # path = data['path']
    # user = "gfilmaster"
    # password = "b32@m451"

    # # Criando as strings de conexão com a porta
    # dsn = f"{server}/{port}:{path}"

    # #fdb.fb_library_name = 'C:/Users/rrgnu/OneDrive/Documentos/MSAtualizaBanco/fbclient.dll'

    # fdb.load_api(f'C:/Program Files/Firebird/Firebird_4_0/fbclient.dll')

    # # Conexões
    # con = fdb.connect(dsn=dsn, user=user, password=password)
    # cursor = con.cursor()

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