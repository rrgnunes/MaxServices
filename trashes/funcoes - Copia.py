import datetime
import os
import mysql.connector
import json
import subprocess
import inspect
import requests
import inspect
from pathlib import Path
import getpass
import xml.etree.ElementTree as ET
import ctypes
import sys
import sqlite3
import fdb
import lzma
import glob
import importlib
from decimal import Decimal
from funcoes_zap import *
import parametros

def print_log(mensagem, caminho_log='log.txt', max_tamanho=1048576):
    # Verifica se a pasta 'log' existe, caso contrário, cria a pasta
    pasta_log = os.path.join(parametros.SCRIPT_PATH, 'log')
    if not os.path.exists(pasta_log):
        os.makedirs(pasta_log)

    # Define o caminho completo do arquivo de log dentro da pasta 'log'
    caminho_completo_log = os.path.join(pasta_log, caminho_log)
    if not '.txt' in caminho_completo_log:
        caminho_completo_log = caminho_completo_log + '.txt'

    agora = datetime.datetime.now()
    timestamp_formatado = agora.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_para_arquivo = agora.strftime('%Y%m%d_%H%M%S')

    nome_funcao = inspect.stack()[1][3]
    nome_script = os.path.basename(inspect.stack()[1].filename)

    mensagem_log = f"{timestamp_formatado} - {nome_script} - {nome_funcao} - {mensagem}"
    print(mensagem_log)

    if os.path.exists(caminho_completo_log) and os.path.getsize(caminho_completo_log) >= max_tamanho:
        novo_nome_arquivo = f"{caminho_completo_log}.{timestamp_para_arquivo}.old"
        os.rename(caminho_completo_log, novo_nome_arquivo)

    with open(caminho_completo_log, 'a') as arquivo_log:
        arquivo_log.write(mensagem_log + '\n')

    padrao_arquivos_old = f"{os.path.basename(caminho_log)}.*.old"
    arquivos_old = list(Path(pasta_log).glob(padrao_arquivos_old))
    arquivos_old.sort(key=os.path.getmtime)

    for arquivo in arquivos_old[:-5]:
        os.remove(arquivo)

def inicializa_conexao_mysql():
    try:
        if parametros.MYSQL_CONNECTION == None:
            parametros.MYSQL_CONNECTION = mysql.connector.connect(
                host=parametros.HOSTMYSQL,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=parametros.BASEMYSQL
            )
        print_log("Conexão com MySQL estabelecida com sucesso.")
    except mysql.connector.Error as err:
        print_log(f"Erro ao conectar ao MySQL: {err}")

def inicializa_conexao_firebird(path_dll):
    try:
        fdb.load_api(path_dll)
        if parametros.FIREBIRD_CONNECTION is None:
            parametros.FIREBIRD_CONNECTION = fdb.connect(
                host=parametros.HOSTFB,
                database=parametros.DATABASEFB,
                user=parametros.USERFB,
                password=parametros.PASSFB,
                port=int(parametros.PORTFB)
            )
        print_log("Conexão com Firebird estabelecida com sucesso.")
    except fdb.fbcore.DatabaseError as err:
        print_log(f"Erro ao conectar ao Firebird: {err}")

def carregar_configuracoes():
    try:
        with open('C:/Users/Public/config.json', 'r') as config_file:
            parametros.CNPJ_CONFIG = json.load(config_file)
            print_log("Configurações carregadas com sucesso.")
            atualizar_conexoes_firebird()
            inicializa_conexao_mysql()
    except Exception as e:
        print_log(f"Erro ao carregar configurações: {e}")

def atualizar_conexoes_firebird():
    for cnpj, dados in parametros.CNPJ_CONFIG['sistema'].items():
        caminho_gbak_firebird_maxsuport = dados['caminho_gbak_firebird_maxsuport']
        path_dll = f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll'
        parametros.DATABASEFB = dados['caminho_base_dados_maxsuport'] 
        parametros.PORTFB = dados['porta_firebird_maxsuport'] 
        parametros.BANCO_SQLITE = os.path.join(os.path.dirname(parametros.DATABASEFB),'dados.db')
        inicializa_conexao_firebird(path_dll)

def verifica_sqlite():
    parametros.PASTA_MAXSUPORT = os.path.join(parametros.SCRIPT_PATH.split('\\')[0],'\\', parametros.SCRIPT_PATH.split('\\')[1])
    if parametros.BANCO_SQLITE == '':
        parametros.BANCO_SQLITE = os.path.join(parametros.PASTA_MAXSUPORT, 'dados', 'dados.db')

    if not os.path.exists(parametros.BANCO_SQLITE):
        comandos_sql = [
            """
            CREATE TABLE IF NOT EXISTS CLIENTE (
                CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
                CLIENTE TEXT (150),
                CNPJCPF TEXT (14)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS CONFIG (
                CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
                ATUALIZAR_BANCO INTEGER DEFAULT (0),
                ATUALIZAR_SISTEMA INTEGER DEFAULT (0),
                VERSAO_NOVA INTEGER DEFAULT (0)
            );
            """,
            """
            INSERT INTO CONFIG (
                       VERSAO_NOVA,
                       ATUALIZAR_SISTEMA,
                       ATUALIZAR_BANCO,
                       CODIGO
                   )
                   VALUES (
                       0,
                       0,
                       0,
                       1
                   );
            """,
            """
            CREATE TABLE IF NOT EXISTS SISTEMA (
                CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
                CODIGOCLIENTE INTEGER REFERENCES CLIENTE (CODIGO) ON DELETE CASCADE,
                SISTEMA_ATIVO INTEGER,
                ALERTA_BLOQUEIO INTEGER,
                SISTEMA_EM_USO_ID INTEGER,
                PASTA_COMPARTILHADA_BACKUP TEXT (200),
                CAMINHO_BASE_DADOS_MAXSUPORT TEXT (200),
                CAMINHO_GBAK_FIREBIRD_MAXSUPORT TEXT (200),
                PORTA_FIREBIRD_MAXSUPORT INTEGER,
                CAMINHO_BASE_DADOS_GFIL TEXT (200),
                CAMINHO_GBAK_FIREBIRD_GFIL TEXT (200),
                PORTA_FIREBIRD_GFIL INTEGER,
                TIMER_MINUTOS_BACKUP INTEGER,
                IP TEXT (15)
            );
            """
        ]
        
        for comando_sql in comandos_sql:
            resultado = consultar_sqlite(comando_sql)
            print_log(f"Tabela criada")

            if not resultado.get('sucesso'):
                print_log(f"Erro ao executar comando SQL: {resultado.get('erro')}")
                break    

def consultar_sqlite(comando_sql):
    try:  
        print(parametros.BANCO_SQLITE)
        conn = sqlite3.connect(parametros.BANCO_SQLITE)
        cursor = conn.cursor()        
        cursor.execute(comando_sql)
        if comando_sql.strip().lower().startswith('select'):
            colunas = [descricao[0] for descricao in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
            retorno = resultados
            print_log(retorno)
            return retorno
        else:
            conn.commit()
            retorno = {"sucesso": True, "mensagem": "Comando executado com sucesso."}
            print_log(retorno)
            return retorno
    except Exception as e:
        retorno = {"sucesso": False, "erro": str(e)}
        print_log(retorno)
        return retorno        
    finally:
        if conn is not None:
            conn.close()

def check_banco_atualizar():
    retorno = consultar_sqlite('select ATUALIZAR_BANCO from config')
    if retorno:
        retorno = retorno[0]['ATUALIZAR_BANCO']
    return retorno

def marca_banco_atualizado():
    consultar_sqlite('UPDATE config set ATUALIZAR_BANCO = 0')

def marca_versao_nova_exe():
    consultar_sqlite('UPDATE config set VERSAO_NOVA = 1')  
    

def atualizar_versao_nova_exe():
    retorno = consultar_sqlite('select ATUALIZAR_SISTEMA from config')
    if retorno:
        retorno = retorno[0]['ATUALIZAR_SISTEMA']
    return retorno   

def marca_versao_atualizada():
    consultar_sqlite('UPDATE config set ATUALIZAR_SISTEMA = 0')

def lerconfig():
    path_config_thread = os.path.join(parametros.SCRIPT_PATH, "config.json")
    if os.path.exists(path_config_thread):
        with open(path_config_thread, 'r') as config_file:
            config_thread = json.load(config_file)
    return config_thread

def SalvaNota(conn, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id):
    try:
        cursor_notafiscal = conn.cursor()
        cursor_notafiscal.execute(f'SELECT * FROM maxservices.notafiscal_notafiscal nn WHERE nn.chave = "{chave}"')
        rows_nota_fiscal = cursor_notafiscal.fetchall()
        if not rows_nota_fiscal:
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
                       WHERE chave = '{chave}'""" 
            
        cursor_notafiscal.execute(sql)
        print_log(f'Salvando nota {tipo_nota} - {chave}')
        cursor_notafiscal.close()
    except Exception as a:
        print_log(a)        

def insert(sql_query, values):
    try:
        if not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION.connect()        
        connection = parametros.MYSQL_CONNECTION
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
    try:
        if not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION.connect()        
        connection = parametros.MYSQL_CONNECTION
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
    try:
        if not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION.connect()

        connection = parametros.MYSQL_CONNECTION
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
        if not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION.connect()
        connection = parametros.MYSQL_CONNECTION
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
    comando = 'start http://maxsuport.com.br/alerta.html'
    subprocess.run(comando, shell=True)

def VerificaVersaoOnline(arquivo_versao):
    versao_online = 0
    try:
        print_log('Bem... Vamos lá')
        url = f"https://maxsuport.com.br/static/update/{arquivo_versao}.txt"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            versao_online = int(response.text)
            print_log('Versão online ' + str(versao_online))
        else:
            print_log(f"Erro ao obter o conteúdo da página: {response.status_code}")
    except Exception as a:
        print_log(a)    
    return versao_online


def extrair_metadados(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT r.rdb$relation_name, rf.rdb$field_name, f.rdb$field_type, f.rdb$field_length, rf.RDB$NULL_FLAG
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
        tipo = row[2]
        tamanho = row[3]
        null = row[4]
        if tabela not in metadados:
            metadados[tabela] = {}
        metadados[tabela][coluna] = {'tipo': tipo, 'tamanho': tamanho, 'null': null}
    return metadados

def mapear_tipo_firebird_para_sql(codigo_tipo):
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
            colunas_sql = []
            for coluna, propriedades in colunas_origem.items():
                tipo = mapear_tipo_firebird_para_sql(int(propriedades['tipo']))
                tamanho = propriedades.get('tamanho', '')
                null = 'NULL'
                if propriedades.get('null', '') != '':
                   null = 'NOT NULL' 
                if propriedades['tipo'] in (8, 16, 35, 13, 7, 10):
                    coluna_def = f"{coluna} {tipo} " + null
                else:
                    coluna_def = f"{coluna} {tipo} " + (f"({tamanho})" if tamanho else "") + " " +  null
                colunas_sql.append(coluna_def)
            colunas_str = ", ".join(colunas_sql)
            scripts_sql.append(f"CREATE TABLE {tabela_origem} ({colunas_str});")
        else:
            for coluna, propriedades in colunas_origem.items():
                tipo = mapear_tipo_firebird_para_sql(int(propriedades['tipo']))
                tamanho = propriedades.get('tamanho', '')
                null = 'NULL'
                if coluna not in metadados_destino[tabela_origem]:
                    if propriedades['tipo'] in (8, 16, 35, 13, 7, 10):
                        coluna_def = f"{coluna} {tipo} "
                    else:
                        coluna_def = f"{coluna} {tipo} " + (f"({tamanho})" if tamanho else "") + " "
                    scripts_sql.append(f"ALTER TABLE {tabela_origem} ADD {coluna_def};")
                else:
                    prop_destino = metadados_destino[tabela_origem][coluna]
                    tipo_destino = mapear_tipo_firebird_para_sql(int(prop_destino['tipo']))
                    tamanho_destino = prop_destino.get('tamanho', '')
                    if tipo != tipo_destino or int(tamanho) > int(tamanho_destino):
                        coluna_def = f"{tipo}" + (f"({tamanho})" if tamanho else "")
                        scripts_sql.append(f"ALTER TABLE {tabela_origem} ALTER COLUMN {coluna} TYPE {coluna_def};")
    return scripts_sql

def executar_scripts_sql(conexao, scripts_sql):
    erros = []
    for script in scripts_sql:
        try:
            cursor = conexao.cursor()
            cursor.execute(script)
            conexao.commit()
        except Exception as e:
            erros.append({'script': script, 'erro': str(e)})
    return erros   

def config_zap(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT ENVIAR_MENSAGEM_ANIVERSARIO,ENVIAR_MENSAGEM_PROMOCAO, 
            ENVIAR_MENSAGEM_DIARIO,MENSAGEM_ANIVERSARIO,
            MENSAGEM_PROMOCAO,MENSAGEM_DIARIO,DIA_MENSAGEM_DIARIA, TIME_MENSAGEM_DIARIA,    
            ULTIMO_ENVIO_ANIVERSARIO,ULTIMO_ENVIO_DIARIO,ULTIMO_ENVIO_PROMOCAO
        FROM CONFIG P
    """)
    colunas = [coluna[0] for coluna in cursor.description]
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    return resultados_em_dicionario[0]

def retorna_pessoas(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT CODIGO,FANTASIA,CELULAR1,ANO_ENVIO_MENSAGEM_ANIVERSARIO FROM PESSOA P 
        WHERE P.CLI = 'S' AND P.ATIVO = 'S'
            AND P.CELULAR1 <> ''''  
            AND EXTRACT(MONTH FROM P.DT_NASC) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(DAY FROM P.DT_NASC) = EXTRACT(DAY FROM CURRENT_DATE)
    """)
    colunas = [coluna[0] for coluna in cursor.description]
    a = cursor.fetchall()
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in a]
    return resultados_em_dicionario

def insere_mensagem_zap(conexao, mensagem, numero):
    codigo = numerador(conexao, 'MENSAGEM_ZAP', 'CODIGO', 'N', '', '')
    data_hora_atual = datetime.datetime.now()
    data_str = data_hora_atual.strftime('%Y-%m-%d')
    hora_str = data_hora_atual.strftime('%H:%M:%S')
    fone = numero[0:2] + numero[3:]
    status = 'PENDENTE'
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO MENSAGEM_ZAP
        (CODIGO, "DATA", MENSAGEM, FONE, STATUS, HORA)
        VALUES(?, ?, ?, ?, ?, ?);
    """, (codigo, data_str, mensagem, fone, status, hora_str))
    conexao.commit()

def numerador(conexao, tabela, campo, filtra, where, valor):
    resultado = 0
    cursor = conexao.cursor()
    if filtra == 'N':
        cursor.execute(f"SELECT MAX({campo}) AS MAIOR FROM {tabela}")
    elif filtra == 'S':
        cursor.execute(f"SELECT MAX({campo}) AS MAIOR FROM {tabela} WHERE {where} = {valor}")
    colunas = [coluna[0] for coluna in cursor.description]
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    if resultados_em_dicionario:
        resultado = resultados_em_dicionario[0]['MAIOR'] + 1
    return resultado

def atualiza_ano_cliente(conexao, codigo, ano):
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE PESSOA
        SET ANO_ENVIO_MENSAGEM_ANIVERSARIO = ?
        WHERE CODIGO = ?;
    """, (ano, codigo))
    conexao.commit()

def atualiza_mensagem(conexao, codigo, status):
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE MENSAGEM_ZAP
        SET STATUS = ?
        WHERE CODIGO = ?;
    """, (status, codigo))
    conexao.commit()

def envia_mensagem(conexao, session):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT CODIGO, MENSAGEM, FONE, STATUS FROM MENSAGEM_ZAP WHERE STATUS = 'PENDENTE'
    """)
    colunas = [coluna[0] for coluna in cursor.description]
    a = cursor.fetchall()
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in a]
    name_session = session

    if parametros.TOKEN_ZAP == '':
        token_gerado = generate_token(name_session)
        parametros.TOKEN_ZAP = token_gerado['token']

    retorno = start_session(name_session)
    if retorno['status'] != 'CONNECTED':
        gera_qrcode(str(retorno['qrcode']).split(',')[1])
        retorno = status_session(name_session)

    for resultado in resultados_em_dicionario:
        if envia_mensagem_zap(session, resultado['FONE'], resultado['MENSAGEM']):
            atualiza_mensagem(conexao, resultado['CODIGO'], 'ENVIADA')
            print_log(f"Mensagem enviada para {resultado['FONE']}")
