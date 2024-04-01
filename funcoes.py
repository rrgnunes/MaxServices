import datetime
import os
from parametros import *
import mysql.connector
import json
import subprocess
import socket
import inspect
import requests
import win32com.client
import inspect
from pathlib import Path
import getpass
import xml.etree.ElementTree as ET
import ctypes
import sys
import sqlite3

# Variáveis globais para os parâmetros do banco de dados
DB_HOST = HOSTMYSQL
DB_USER = USERMYSQL
DB_PASSWORD = PASSMYSQL
DB_DATABASE = BASEMYSQL

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
arquivo_db = 'c:/maxsuport/dados/dados.db'

def consultar_sqlite(consulta_sql):
    """
    Conecta a um banco de dados SQLite, executa uma consulta SQL, e retorna os resultados como uma lista de dicionários.
    
    :param arquivo_db: Caminho para o arquivo do banco de dados SQLite.
    :param consulta_sql: String contendo a consulta SQL a ser executada.
    :return: Resultados da consulta como uma lista de dicionários.
    """
    conexao = sqlite3.connect(arquivo_db)
    # Configurar a conexão para retornar linhas como dicionários
    conexao.row_factory = sqlite3.Row
    
    cursor = conexao.cursor()

    try:
        if 'select' in consulta_sql.lower():
            cursor.execute(consulta_sql)
            # Recuperar os resultados usando um dicionário
            resultados = [dict(linha) for linha in cursor.fetchall()]
            return resultados
        else:
            cursor.execute(consulta_sql)
            conexao.commit()
            return None
        
    except sqlite3.Error as erro:
        print(f"Ocorreu um erro ao executar a consulta SQL: {erro}")
        return None
    finally:
        conexao.close()

def check_banco_atualizar():
    retorno = consultar_sqlite('select ATUALIZAR_BANCO from config')
    if retorno is not None:
        retorno = retorno[0]['ATUALIZAR_BANCO']
    return retorno

def marca_banco_atualizado():
    consultar_sqlite('UPDATE config set ATUALIZAR_BANCO = 0')

def marca_versao_nova_exe():
    consultar_sqlite('UPDATE config set VERSAO_NOVA = 1')  

def atualizar_versao_nova_exe():
    retorno = consultar_sqlite('select ATUALIZAR_SISTEMA from config')
    if retorno is not None:
        retorno = retorno[0]['ATUALIZAR_SISTEMA']
    return retorno   


def lerconfig():
    path_config_thread = SCRIPT_PATH + "/config.json"
    if os.path.exists(path_config_thread):
        with open(path_config_thread, 'r') as config_file:
            config_thread = json.load(config_file)
    return config_thread

def SalvaNota(conn,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id):
        try:
            cursor_notafiscal = conn.cursor()
            cursor_notafiscal.execute(f'select * from maxservices.notafiscal_notafiscal nn where nn.chave = "{chave}"')
            rows_nota_fiscal = cursor_notafiscal.fetchall()
            if len(rows_nota_fiscal) == 0:
                sql = f"""INSERT INTO maxservices.notafiscal_notafiscal 
                    (numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento,
                        cliente_id, contador_id)
                    VALUES('{numero}', '{chave}', '{tipo_nota}', '{serie}',
                            '{data_nota}', '{xml}', '{xml_cancelamento}',
                            '{cliente_id}', '{contador_id}')"""
            else:
                sql = f"""UPDATE maxservices.notafiscal_notafiscal SET 
                            numero = '{numero}',
                            chave = '{chave}',
                            tipo_nota='{tipo_nota}',
                            serie='{serie}',
                            data_nota='{data_nota}',
                            xml='{xml}',
                            xml_cancelamento='{xml_cancelamento}',
                            cliente_id='{cliente_id}',
                            contador_id='{contador_id}'
                           where chave = '{chave}'""" 
            
            cursor_notafiscal.execute(sql)
            print_log(f'Salvando nota {tipo_nota} - {chave}')
            cursor_notafiscal.close()
        except Exception as a:
            print_log(a)        

def get_db_connection():
    # Função auxiliar para obter uma conexão com o banco de dados
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )

def insert(sql_query, values):
    # Função para executar uma operação de inserção no banco de dados
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(sql_query, values)
        connection.commit()

        print_log("Inserção bem-sucedida!")

    except Exception as e:
        print_log(f"Erro durante a inserção: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete(sql_query, values):
    # Função para executar uma operação de exclusão no banco de dados
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(sql_query, values)
        connection.commit()

        print_log("Exclusão bem-sucedida!")

    except Exception as e:
        print_log(f"Erro durante a exclusão: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update(sql_query, values):
    # Função para executar uma operação de atualização no banco de dados
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(sql_query, values)
        connection.commit()

        print_log("Atualização bem-sucedida!")

    except Exception as e:
        print_log(f"Erro durante a atualização: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def select(sql_query, values=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if values:
            cursor.execute(sql_query, values)
        else:
            cursor.execute(sql_query)

        result = cursor.fetchall()

        if result:
            return result
        else:
            print_log("Nenhum resultado encontrado.")
            return []

    except Exception as e:
        print_log(f"Erro durante a consulta: {e}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()        


def exibe_alerta(aviso):
    # Envia Alerta
    # Configurar as informações do servidor
    host = 'localhost'  # Endereço IP ou nome do host do servidor
    port = 3060  # Porta do servidor

    # Criar um objeto de socket
    client_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)

    # Conectar ao servidor
    client_socket.connect((host, port))
    print_log(f"Conectado com o alerta - MaxServices")
    # Envia comando
    client_socket.send(aviso.encode('utf-8'))

    # Receber a resposta do servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print_log(f"Resposta do servidor {resposta} - MaxServices")

    # Fechar a conexão
    client_socket.close()    


def VerificaVersaoOnline(arquivo_versao):
    versao_online = 0
    try:
        
        print_log('Bem... Vamos lá')

        # Substitua pelo URL da página que deseja obter o conteúdo
        url = f"https://maxsuport.com.br/static/update/{arquivo_versao}.txt"

        # Faz a requisição GET para a página
        response = requests.get(url, timeout=5)

        # Verifica se a requisição foi bem-sucedida (código de status 200)
        if response.status_code == 200:
            # Obtém o conteúdo da página como uma string
            versao_online = int(response.text)
            print_log('Versão online ' + str(versao_online))

        else:
            print_log("Erro ao obter o conteúdo da página:",
                response.status_code)
    except Exception as a:
        print_log(a)    
    
    return versao_online

def cria_tarefa_login(nome_executavel):
    usuario_atual = getpass.getuser()
    # Conecta ao Agendador de Tarefas
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    
    # Verifica se a tarefa já existe
    try:
        root_folder.GetTask(f'{nome_executavel}NoLogin')
        print_log(f"A tarefa '{nome_executavel}NoLogin' já existe.")
        return  # Se a tarefa existir, termina a função
    except Exception as e:
        print_log(f"A tarefa '{nome_executavel}NoLogin' não existe. Será criada.")

    # Define informações básicas da tarefa
    task_definition = scheduler.NewTask(0)
    task_definition.RegistrationInfo.Description = f'Executa {nome_executavel}.exe ao logar'
    task_definition.RegistrationInfo.Author = 'Admin'

    # Dispara no logon do usuário
    trigger = task_definition.Triggers.Create(1)  # 1 é TASK_TRIGGER_LOGON
    trigger.StartBoundary = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Define a ação para executar MaxServices.exe
    action = task_definition.Actions.Create(0)  # 0 é TASK_ACTION_EXEC
    action.Path = f'C:/maxsuport/{nome_executavel}.exe'
    action.WorkingDirectory = 'C:/maxsuport/'

    # Configura a tarefa para ser executada com o máximo de privilégios
    task_definition.Principal.RunLevel = 1  # TASK_RUNLEVEL_HIGHEST
    task_definition.Principal.UserId = usuario_atual

    # Registra a tarefa (aqui você pode especificar a conta de usuário e senha, se necessário)
    task_folder = root_folder  # Para este exemplo, vamos registrar na pasta raiz do Agendador de Tarefas
    task_folder.RegisterTaskDefinition(
        f'{nome_executavel}NoLogin',  # Nome da Tarefa
        task_definition,
        6,  # TASK_CREATE_OR_UPDATE
        usuario_atual,  # Usuário (None = usuário atual)
        None,  # Senha (None = usuário atual)
        3,  # TASK_LOGON_INTERACTIVE_TOKEN
        ''  # SDDL vazio para configurações padrão de segurança
    )
    print_log("Tarefa criada com sucesso.")

def criar_tarefa_minuto(nome_executavel):

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    while not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    usuario_atual = getpass.getuser()
    # Conectar ao Agendador de Tarefas do Windows
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # Define informações básicas da tarefa
    task_def = scheduler.NewTask(0)  # 0 indica criação de uma nova tarefa

    # Cria um gatilho para iniciar a tarefa a cada minuto
    INTERVALO_MINUTOS = 1
    start_trigger = task_def.Triggers.Create(1)  # TASK_TRIGGER_TIME
    start_trigger.Repetition.Interval = f"PT{INTERVALO_MINUTOS}M"
    start_trigger.Repetition.Duration = ""  # Duração de 1 dia, mas você pode ajustar conforme necessário
    start_trigger.StartBoundary = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Cria uma ação para a tarefa que executa o MaxServices.exe
    action = task_def.Actions.Create(0)  # TASK_ACTION_EXEC
    action.Path = f'c:/maxsuport/{nome_executavel}.exe'
    action.WorkingDirectory = 'C:/maxsuport/'

    # Define informações adicionais da tarefa
    task_def.RegistrationInfo.Description = f'Executa {nome_executavel}.exe a cada minuto'
    task_def.Principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN
    task_def.Settings.DisallowStartIfOnBatteries = False
    task_def.Settings.StopIfGoingOnBatteries = False
    task_def.Settings.ExecutionTimeLimit = "PT0S"  # Sem limte de tempo de execução
    task_def.Principal.UserId = usuario_atual
    task_def.Principal.RunLevel = 1 # TASK_RUNLEVEL_HIGHESTo

    # Registra a tarefa
    root_folder = scheduler.GetFolder("\\")
    nome_tarefa = "MaxServicesMinuto"

    try:

        root_folder.RegisterTaskDefinition(
            nome_tarefa,  # Nome da tarefa
            task_def,
            6,  # TASK_CREATE_OR_UPDATE
            usuario_atual,  # Usuário (None usa o usuário atual)
            None,  # Senha (None para usuário atual ou quando não necessário)
            3  # TASK_LOGON_INTERACTIVE_TOKEN
        )
        print_log(f"Tarefa '{nome_tarefa}' criada com sucesso.")    
    except Exception as a:
        print_log(a)

def create_task_from_xml(task_name):
    """ 
    Create a scheduled task in Windows Task Scheduler using an XML file.
    Parameters:
    - xml_path (str): Path to the XML file.
    - task_name (str): Name of the task to be created.
    Returns:
    - stdout (str): Output from the schtasks command.
    - stderr (str): Error (if any) from the schtasks command.
    """
    # Definir o nome do arquivo XML
    arquivo_xml = 'c:/maxsuport/SERVER/task.xml'
    arquivo_xml_novo = f'c:/maxsuport/SERVER/task_{task_name}.xml'

    # Definir as variáveis
    nome_agenda = task_name
    data_hora_agora = datetime.datetime.now().isoformat()

    # Ler o arquivo XML
    with open(arquivo_xml, 'r', encoding='utf-8') as file:
        xml_string = file.read()

    # Substituir as variáveis no conteúdo do XML
    xml_string = xml_string.replace('{nome_agenda}', nome_agenda)
    xml_string = xml_string.replace('{data_hora_agora}', data_hora_agora)

    # Parsear a string XML modificada de volta para um objeto ElementTree
    root = ET.ElementTree(ET.fromstring(xml_string))

    # Salvar o XML modificado. Usamos 'utf-16' como a codificação para garantir que o BOM seja incluído
    with open(arquivo_xml_novo, 'wb') as file:
        root.write(file)        

    cmd = ['schtasks', '/create', '/xml', arquivo_xml_novo, '/tn', task_name]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.stdout, result.stderr        

def print_log(mensagem, caminho_log='log.txt', max_tamanho=1048576):
    """Escreve uma mensagem de log em um arquivo sem exceder o tamanho máximo especificado, incluindo detalhes adicionais.
    
    Args:
        mensagem (str): Mensagem a ser logada.
        caminho_log (str): Caminho do arquivo de log.
        max_tamanho (int): Tamanho máximo do arquivo de log em bytes. Padrão é 1MB.
    """
    caminho_log = f'{SCRIPT_PATH}/{caminho_log}'
    # Obtém a data e hora atual
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Obtém o nome da função que chamou escrever_log
    nome_funcao = inspect.stack()[1][3]

    # Obtém o nome do script
    nome_script = os.path.basename(inspect.stack()[1].filename)

    # Monta a mensagem de log com as informações adicionais
    mensagem_log = f"{agora} - {nome_script} - {nome_funcao} - {mensagem}"
    print(mensagem_log)

    # Verifica se o arquivo de log existe e se excede o tamanho máximo
    if Path(caminho_log).exists() and os.path.getsize(caminho_log) >= max_tamanho:
        # Arquiva o log atual e cria um novo
        os.rename(caminho_log, f"{caminho_log}.old")
    
    # Escreve a mensagem no arquivo de log
    with open(caminho_log, 'a') as arquivo_log:
        arquivo_log.write(mensagem_log + '\n')

def extrair_metadados(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT r.rdb$relation_name, rf.rdb$field_name, f.rdb$field_type, f.rdb$field_length,rf.RDB$NULL_FLAG
        FROM rdb$relations r
        JOIN rdb$relation_fields rf ON r.rdb$relation_name = rf.rdb$relation_name
        JOIN rdb$fields f ON rf.rdb$field_source = f.rdb$field_name
        WHERE r.rdb$view_blr IS NULL 
        AND (r.rdb$system_flag IS NULL OR r.rdb$system_flag = 0);
    """)
    
    metadados = {}
    for row in cursor.fetchall():
        tabela = row[0].strip()
        coluna = row[1].strip()
        tipo = row[2]  # Isso retorna um código de tipo, você deve mapear para um tipo de dado real
        tamanho = row[3]
        null = row[4]
        if tabela not in metadados:
            metadados[tabela] = {}
        metadados[tabela][coluna] = {'tipo': tipo, 'tamanho': tamanho,'null':null}
    return metadados

def mapear_tipo_firebird_para_sql(codigo_tipo):
    """
    Função para mapear os códigos numéricos dos tipos de dados do Firebird para tipos de dados SQL.
    """
    mapa_tipos = {
        261: "BLOB",
        14: "CHAR",
        40: "CSTRING",
        11: "D_FLOAT",
        27: "DOUBLE",
        10: "FLOAT",
        16: "BIGINT",
        8: "INTEGER",
        9: "QUAD",
        7: "SMALLINT",
        12: "DATE",
        13: "TIME",
        35: "TIMESTAMP",
        37: "VARCHAR",
    }
    return mapa_tipos.get(codigo_tipo, "UNKNOWN")

def gerar_scripts_diferencas(metadados_origem, metadados_destino):
    scripts_sql = []

    for tabela_origem, colunas_origem in metadados_origem.items():
        if tabela_origem not in metadados_destino:
            # Criação de tabela que não existe no destino
            colunas_sql = []
            for coluna, propriedades in colunas_origem.items():
                tipo = mapear_tipo_firebird_para_sql(int(propriedades['tipo']))
                tamanho = propriedades.get('tamanho', '')
                null = 'NULL'
                if propriedades.get('null', '') != '':
                   null = 'NOT NULL' 
                if propriedades['tipo'] in (8,16,35,13,7,10) :
                    coluna_def = f"{coluna} {tipo} " + null
                else:
                    coluna_def = f"{coluna} {tipo} " + (f"({tamanho})" if tamanho else "") + " " +  null
                colunas_sql.append(coluna_def)
            colunas_str = ", ".join(colunas_sql)
            scripts_sql.append(f"CREATE TABLE {tabela_origem} ({colunas_str});")
        else:
            # Tabela existe, verificar colunas
            for coluna, propriedades in colunas_origem.items():
                tipo_origem = mapear_tipo_firebird_para_sql(int(propriedades['tipo']))  # Garante a definição de 'tipo_origem'
                tamanho_origem = propriedades.get('tamanho', '')
                if coluna not in metadados_destino[tabela_origem]:
                    # Adiciona coluna que não existe no destino
                    coluna_def = f"{coluna} {tipo_origem}" + (f"({tamanho_origem})" if tamanho_origem else "")
                    scripts_sql.append(f"ALTER TABLE {tabela_origem} ADD {coluna_def};")
                else:
                    # Coluna existe, verificar tipo e tamanho
                    prop_destino = metadados_destino[tabela_origem][coluna]
                    tipo_destino = mapear_tipo_firebird_para_sql(int(prop_destino['tipo']))
                    tamanho_destino = prop_destino.get('tamanho', '')
                    # Correção da referência à variável 'tipo_origem' e 'tamanho_origem'
                    if tipo_origem != tipo_destino or int(tamanho_origem) > int(tamanho_destino):
                        coluna_def = f"{tipo_origem}" + (f"({tamanho_origem})" if tamanho_origem else "")
                        # Dependendo do SGBD, a sintaxe de alteração pode variar. Verifique a compatibilidade.
                        scripts_sql.append(f"ALTER TABLE {tabela_origem} ALTER COLUMN {coluna} TYPE {coluna_def};")

    return scripts_sql

def executar_scripts_sql(conexao, scripts_sql):
    erros = []  # Lista para armazenar os erros

    for script in scripts_sql:
        try:
            # Executar o script SQL
            cursor = conexao.cursor()
            cursor.execute(script)
            conexao.commit()  # Efetivar a transação se o script for executado com sucesso
        except Exception as e:
            # Se ocorrer um erro, armazene o script e a mensagem de erro na lista de erros
            erros.append({'script': script, 'erro': str(e)})
    
    return erros   