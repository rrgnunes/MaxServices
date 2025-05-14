import datetime
import os
import mysql.connector
import inspect
import sys
import fdb
import parametros
import subprocess
import configparser
from pathlib import Path
from mysql.connector import Error
from funcoes_zap import *
from typing import Optional, Tuple


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
        
def envia_audio_texto_api_comando(tipo, dados, cnpj_empresa):
    
    if tipo == 'texto':
        url = "http://10.105.96.102:8000/processar_texto/"

        # Exemplo de payload
        payload = {
            "cnpj_empresa": cnpj_empresa,
            "texto": dados
        }

        # Envia os dados como JSON
        response = requests.post(url, json=payload)
    else:
        
        url = "http://10.105.96.102:8000/processar_audio/"
        
        with open(dados, "rb") as f:
            files = {"arquivo": ("audio.wav", f, "audio/wav")}
            data = {"cnpj_empresa": cnpj_empresa}  # Adiciona o CNPJ no envio
            response = requests.post(url, files=files, data=data)

        print("📨 Resposta da API:", response.text)
    
    return response.text    

def inicializa_conexao_mysql():
    try:
        if parametros.MYSQL_CONNECTION == None or not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION = mysql.connector.connect(
                host=parametros.HOSTMYSQL,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=parametros.BASEMYSQL,
                auth_plugin='mysql_native_password',  # Força o uso do plugin correto
                connection_timeout=15
            )
        print_log("Conexão com MySQL estabelecida com sucesso.")
    except mysql.connector.Error as err:
        print_log(f"Erro ao conectar ao MySQL: {err}")

def inicializa_conexao_firebird():
    try:
        fdb.load_api(parametros.PATHDLL)
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

def carrega_arquivo_config():
    with open(f'{parametros.SCRIPT_PATH}/config.json', 'r') as config_file:
            parametros.CNPJ_CONFIG = json.load(config_file)

def carregar_configuracoes():
    try:
        carrega_arquivo_config()
        print_log("Configurações carregadas com sucesso.")
        inicializa_conexao_mysql()
        atualizar_conexoes_firebird()
    except Exception as e:
        print_log(f"Erro ao carregar configurações: {e}")

def atualizar_conexoes_firebird():
    for cnpj, dados in parametros.CNPJ_CONFIG['sistema'].items():
        if (dados['caminho_base_dados_maxsuport'] == None) or (dados['caminho_base_dados_maxsuport'] == 'None'):
            continue
        caminho_gbak_firebird_maxsuport = dados['caminho_gbak_firebird_maxsuport']
        parametros.PATHDLL = f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll'
        parametros.DATABASEFB = dados['caminho_base_dados_maxsuport'] 
        parametros.PORTFB = dados['porta_firebird_maxsuport'] 
        inicializa_conexao_firebird()

def SalvaNota(conn, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie):
    try:
        cursor_notafiscal = conn.cursor()
        cursor_notafiscal.execute(f'SELECT * FROM maxservices.notafiscal_notafiscal nn WHERE nn.chave = "{chave}"')
        rows_nota_fiscal = cursor_notafiscal.fetchall()
        if not rows_nota_fiscal:
            sql = f"""INSERT INTO maxservices.notafiscal_notafiscal 
                (numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento,
                    cliente_id, contador_id, ie)
                VALUES('{numero}', '{chave}', '{tipo_nota}', '{serie}',
                        '{data_nota}', '{xml}', '{xml_cancelamento}',
                        '{cliente_id}', '{contador_id}', '{cliente_ie}')"""
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
                        contador_id='{contador_id}',
                        ie= '{cliente_ie}'
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
        if parametros.MYSQL_CONNECTION.is_connected():
            cursor.close()
            parametros.MYSQL_CONNECTION.close()
        if connection.is_connected():
            connection.close()        

def selectfb(sql_query, values=None):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()   
        connection = parametros.FIREBIRD_CONNECTION
        cursor = connection.cursor()
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
        print_log("Comando OK")          

def insertfb(sql_query, values):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()   
        connection = parametros.FIREBIRD_CONNECTION
        cursor = connection.cursor()
        cursor.execute(sql_query, values)
        connection.commit()
        print_log("Inserção bem-sucedida!")
    except Exception as e:
        print_log(f"Erro durante a inserção: {e}")
    finally:
        print_log("Comando OK")                

def deletefb(sql_query, values):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()
        connection = parametros.FIREBIRD_CONNECTION
        cursor = connection.cursor()
        cursor.execute(sql_query, values)
        connection.commit()
        print_log("Exclusão bem-sucedida!")
    except Exception as e:
        print_log(f"Erro durante a exclusão: {e}")
    finally:
        print_log("Comando OK")             

def updatefb(sql_query, values):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()

        connection = parametros.FIREBIRD_CONNECTION
        cursor = connection.cursor()
        cursor.execute(sql_query, values)
        connection.commit()
        print_log("Atualização bem-sucedida!")
    except Exception as e:
        print_log(f"Erro durante a atualização: {e}")
    finally:
        print_log("Comando OK")           

def selectfb(sql_query, values=None):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()
        connection = parametros.FIREBIRD_CONNECTION
        cursor = connection.cursor()
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
        print_log("Comando OK")          

def exibe_alerta():
    comando = 'start http://maxsuport.com/alerta'
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

def inicializa_conexao_mysql_replicador():
    try:
        if parametros.MYSQL_CONNECTION_REPLICADOR == None:
            parametros.MYSQL_CONNECTION_REPLICADOR = mysql.connector.connect(
                host=parametros.HOSTMYSQL_REP,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=parametros.BASEMYSQL_REP,
                auth_plugin='mysql_native_password'
            )
        print_log(f"Conexão com MySQL estabelecida com sucesso.")
    except mysql.connector.Error as err:
        print_log(f"Erro ao conectar ao MySQL: {err}")

def extrair_metadados_mysql(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            COLUMN_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM
            INFORMATION_SCHEMA.COLUMNS
        WHERE
            TABLE_SCHEMA = DATABASE()
        ORDER BY
            TABLE_NAME, COLUMN_NAME
    """)

    metadados = {}
    for row in cursor.fetchall():
        tabela = row[0]
        coluna = row[1]
        tipo = row[2].split('(')[0]
        is_nullable = 'NOT NULL' if row[3] == 'NO' else ''
        tamanho = row[5] if row[5] else ''
        precisao = row[6] if row[6] else None
        escala = row[7] if row[7] else None

        if tabela not in metadados:
            metadados[tabela] = {}
        metadados[tabela][coluna] = {'tipo': tipo, 'tamanho': tamanho, 'null': is_nullable, 'precisao': precisao, 'escala': escala}
    
    return metadados

def mapear_tipo_firebird_mysql(tipo, precisao=None, escala=None, tamanho=None):
    tipo = tipo.upper()
    if 'CHAR' in tipo:
        tipo = tipo.split('(')[0]
    if ('VARCHAR') == tipo and (tamanho >= 10000):
        tipo = 'TEXT'
    if 'BIGINT' in tipo:
        tipo = 'BIGINT'
    if 'DECIMAL' in tipo:
        if precisao == 4:
            precisao = 15

    mapa_tipos = {
    'SMALLINT': 'SMALLINT',
    'INTEGER': 'INT',
    'INT': 'INT',
    'NUMERIC': f'DECIMAL({precisao},{str(escala).replace("-", "")})' if precisao and escala else 'DECIMAL',
    'DECIMAL': f'DECIMAL({precisao},{str(escala).replace("-", "")})' if precisao and escala else 'DECIMAL',
    'QUAD': 'BIGINT',
    'FLOAT': 'FLOAT',
    'DATE': 'DATE',
    'TIME': 'TIME',
    'CHAR': f'CHAR({tamanho})' if tamanho else 'CHAR',
    'BIGINT': 'BIGINT',
    'DOUBLE': 'DOUBLE',
    'TIMESTAMP': 'DATETIME',
    'DATETIME': 'DATETIME',
    'VARCHAR': f'VARCHAR({tamanho})' if tamanho else 'VARCHAR',
    'CSTRING': f'VARCHAR({tamanho})' if tamanho else 'VARCHAR',
    'BLOB SUB_TYPE 0': 'LONGBLOB',
    'BLOB SUB_TYPE 1': 'MEDIUMBLOB',
    'MEDIUMBLOB': 'MEDIUMBLOB',
    'BLOB': 'BLOB',
    'LONGBLOB': 'LONGBLOB'
    }
    return mapa_tipos.get(tipo, 'TEXT')

def gerar_scripts_diferentes_mysql(metadados_origem, metadados_destino):
    scripts_sql = []

    # Verificar tabelas que existem na origem, mas não no destino
    for tabela_origem, colunas_origem in metadados_origem.items():
        if tabela_origem not in metadados_destino:
            colunas_sql = []
            for coluna, propriedades in colunas_origem.items():
                tipo = mapear_tipo_firebird_mysql(propriedades['tipo'], propriedades['precisao'], propriedades['escala'], propriedades['tamanho'])
                # null = propriedades.get('null', '')
                null = ''

                coluna_def = f"`{coluna}` {tipo} {null}"
                colunas_sql.append(coluna_def)
            colunas_str = ", ".join(colunas_sql)
            scripts_sql.append(f"CREATE TABLE `{tabela_origem}` ({colunas_str});")

    # Verificar colunas que existem na origem, mas não no destino ou que têm propriedades diferentes
    for tabela_origem, colunas_origem in metadados_origem.items():
        if tabela_origem in metadados_destino:
            for coluna, propriedades in colunas_origem.items():
                tipo = mapear_tipo_firebird_mysql(propriedades['tipo'], propriedades['precisao'], propriedades['escala'], propriedades['tamanho'])
                # null = propriedades.get('null', '')
                null = ''

                if coluna not in metadados_destino[tabela_origem]:
                    coluna_def = f"`{coluna}` {tipo} {null}"
                    scripts_sql.append(f"ALTER TABLE `{tabela_origem}` ADD {coluna_def};")
                else:
                    prop_destino = metadados_destino[tabela_origem][coluna]
                    tipo_destino = mapear_tipo_firebird_mysql(prop_destino['tipo'], prop_destino['precisao'], prop_destino['escala'], prop_destino['tamanho'])
                    # null_destino = prop_destino.get('null', '')
                    null_destino = ''

                    if tipo != tipo_destino or null != null_destino:
                        coluna_def = f"`{coluna}` {tipo} {null}"
                        scripts_sql.append(f"ALTER TABLE `{tabela_origem}` MODIFY COLUMN {coluna_def};")
    
    return scripts_sql

def executar_scripts_mysql(conexao_mysql, scripts_sql, nome_servico):
    erros = []
    for script in scripts_sql:
        try:
            cursor = conexao_mysql.cursor()
            cursor.execute(script)
            conexao_mysql.commit()
            print_log(f'Comando executado: {script}', nome_servico)
        except Exception as e:
            conexao_mysql.rollback()
            erros.append({'script': script, 'erro': str(e)})
    return erros

def extrair_metadados(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
                        SELECT
                        RF.RDB$RELATION_NAME,RF.RDB$FIELD_NAME FIELD_NAME,f.RDB$FIELD_PRECISION,f.RDB$FIELD_SCALE,F.RDB$FIELD_LENGTH,
                        CASE F.RDB$FIELD_TYPE
                            WHEN 7 THEN
                            CASE F.RDB$FIELD_SUB_TYPE
                                WHEN 0 THEN 'SMALLINT'
                                WHEN 1 THEN 'NUMERIC(' || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                                WHEN 2 THEN 'DECIMAL'
                            END
                            WHEN 8 THEN
                            CASE F.RDB$FIELD_SUB_TYPE
                                WHEN 0 THEN 'INTEGER'
                                WHEN 1 THEN 'NUMERIC('  || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                                WHEN 2 THEN 'DECIMAL'
                            END
                            WHEN 9 THEN 'QUAD'
                            WHEN 10 THEN 'FLOAT'
                            WHEN 12 THEN 'DATE'
                            WHEN 13 THEN 'TIME'
                            WHEN 14 THEN 'CHAR(' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ') '
                            WHEN 16 THEN
                            CASE F.RDB$FIELD_SUB_TYPE
                                WHEN 0 THEN 'BIGINT'
                                WHEN 1 THEN 'NUMERIC'
                                WHEN 2 THEN 'DECIMAL'
                            END
                            WHEN 27 THEN 'DOUBLE'
                            WHEN 35 THEN 'TIMESTAMP'
                            WHEN 37 THEN 'VARCHAR'
                            WHEN 40 THEN 'CSTRING' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ')'
                            WHEN 45 THEN 'BLOB_ID'
                            WHEN 261 THEN 'BLOB SUB_TYPE ' || F.RDB$FIELD_SUB_TYPE
                            ELSE 'RDB$FIELD_TYPE: ' || F.RDB$FIELD_TYPE || '?'
                        END FIELD_TYPE,
                        IIF(COALESCE(RF.RDB$NULL_FLAG, 0) = 0, NULL, 'NOT NULL') FIELD_NULL,
                        CH.RDB$CHARACTER_SET_NAME FIELD_CHARSET,
                        DCO.RDB$COLLATION_NAME FIELD_COLLATION,
                        COALESCE(RF.RDB$DEFAULT_SOURCE, F.RDB$DEFAULT_SOURCE) FIELD_DEFAULT,
                        F.RDB$VALIDATION_SOURCE FIELD_CHECK,
                        RF.RDB$DESCRIPTION FIELD_DESCRIPTION
                        FROM RDB$RELATION_FIELDS RF
                        JOIN RDB$FIELDS F ON (F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE)
                        LEFT OUTER JOIN RDB$CHARACTER_SETS CH ON (CH.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID)
                        LEFT OUTER JOIN RDB$COLLATIONS DCO ON ((DCO.RDB$COLLATION_ID = F.RDB$COLLATION_ID) AND (DCO.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID))
                        WHERE (COALESCE(RF.RDB$SYSTEM_FLAG, 0) = 0)
                        ORDER BY RF.RDB$RELATION_NAME,RF.RDB$FIELD_NAME
    """)
    
    metadados = {}
    results = cursor.fetchall()
    for row in results:
        tabela = row[0].strip()
        coluna = row[1].strip() 
        tipo = row[5]
        tamanho = row[4]
        null = row[6]
        if null is None:
            null = '' 

        precisao = row[2]#RDB$FIELD_PRECISION
        escala = row[3] #RDB$FIELD_SCALE       

        if tabela not in metadados:
            metadados[tabela] = {}
        metadados[tabela][coluna] = {'tipo': tipo, 'tamanho': tamanho, 'null': null,'precisao':precisao,'escala':escala}
    return metadados

def mapear_tipo_firebird_para_sql(codigo_tipo):
    mapa_tipos = {
        261: "BLOB",
        14: "CHAR",
        40: "CSTRING",
        11: "D_FLOAT",
        27: "DOUBLE",
        10: "FLOAT",
        16: "DECIMAL",
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

    # Verificar tabelas que existem na origem, mas não no destino
    for tabela_origem, colunas_origem in metadados_origem.items():
        if tabela_origem not in metadados_destino:
            colunas_sql = []
            for coluna, propriedades in colunas_origem.items():
                tipo = propriedades['tipo']
                tamanho = propriedades.get('tamanho', '')
                null = propriedades.get('null', '')

                if tipo in ('INTEGER', 'NUMERIC', 'DECIMAL', 'FLOAT', 'SMALLINT', 'DATE', 'TIME', 'DOUBLE', 'TIMESTAMP', 'BLOB SUB_TYPE 1', 'BLOB SUB_TYPE 0'):
                    if tipo in ('INTEGER', 'SMALLINT', 'DATE', 'TIME', 'TIMESTAMP', 'BLOB SUB_TYPE 1', 'BLOB SUB_TYPE 0'):
                        coluna_def = f"{coluna} {tipo} {null}"
                    else:
                        coluna_def = f"{coluna} {tipo}({propriedades['precisao']},{str(propriedades['escala']).replace('-','')}) {null}"
                else:
                    coluna_def = f"{coluna} {tipo} " + (f"({tamanho})" if tamanho else "") + f" {null}"

                colunas_sql.append(coluna_def)
            colunas_str = ", ".join(colunas_sql)
            scripts_sql.append(f"CREATE TABLE {tabela_origem} ({colunas_str});")

    # Verificar colunas que existem na origem, mas não no destino ou que têm propriedades diferentes
    for tabela_origem, colunas_origem in metadados_origem.items():
        if tabela_origem in metadados_destino:
            for coluna, propriedades in colunas_origem.items():
                tipo = propriedades['tipo']
                tamanho = propriedades.get('tamanho', '')
                null = propriedades.get('null', '')

                if coluna not in metadados_destino[tabela_origem]:
                    if tipo in ('INTEGER', 'NUMERIC', 'DECIMAL', 'FLOAT', 'SMALLINT', 'DATE', 'TIME', 'DOUBLE', 'TIMESTAMP', 'BLOB SUB_TYPE 1', 'BLOB SUB_TYPE 0'):
                        if tipo in ('INTEGER', 'SMALLINT', 'DATE', 'TIME', 'TIMESTAMP', 'BLOB SUB_TYPE 1', 'BLOB SUB_TYPE 0'):
                            coluna_def = f"{coluna} {tipo} {null}"
                        else:
                            coluna_def = f"{coluna} {tipo}({propriedades['precisao']},{str(propriedades['escala']).replace('-','')}) {null}"
                    else:
                        coluna_def = f"{coluna} {tipo} " + (f"({tamanho})" if tamanho else "") + f" {null}"

                    scripts_sql.append(f"ALTER TABLE {tabela_origem} ADD {coluna_def};")
                else:
                    prop_destino = metadados_destino[tabela_origem][coluna]
                    tipo_destino = prop_destino['tipo']
                    tamanho_destino = prop_destino.get('tamanho', '')
                    null_destino = prop_destino.get('null', '')

                    if tipo != tipo_destino or tamanho != tamanho_destino or null != null_destino:
                        if tipo in ('INTEGER', 'NUMERIC', 'DECIMAL', 'FLOAT', 'SMALLINT', 'DATE', 'TIME', 'DOUBLE', 'TIMESTAMP'):
                            if tipo in ('INTEGER', 'SMALLINT', 'DATE', 'TIME', 'TIMESTAMP'):
                                coluna_def = f"{tipo} {null}"
                            else:
                                coluna_def = f"{tipo}({propriedades['precisao']},{str(propriedades['escala']).replace('-','')}) {null}"
                        else:
                            coluna_def = f"{tipo} " + (f"({tamanho})" if tamanho else "") + f" {null}"

                        scripts_sql.append(f"ALTER TABLE {tabela_origem} ALTER COLUMN {coluna} TYPE {coluna_def};")
    
    return scripts_sql

def executar_scripts_sql(conexao, scripts_sql, nome_servico):
    erros = []
    for script in scripts_sql:
        try:
            cursor = conexao.cursor()
            cursor.execute(script)
            conexao.commit()
            print_log(f'Executado: {script}', nome_servico)
        except Exception as e:
            erros.append({'script': script, 'erro': str(e)})
    return erros   

def salva_mensagem_remota(conn, data, mensagem, fone, status, cliente_id, nome_servico, retorno):
    salvo = False
    try:
        cur_zap = conn.cursor()
        sql = f"INSERT INTO maxservices.zap_zap (datahora, mensagem, fone, status, cliente_id, retorno) values ('{data}', '{mensagem}', '{fone}', '{status}', '{cliente_id}', '{retorno}')"
        cur_zap.execute(sql)
        print_log(f'Salvando mensagem da empresa: {cliente_id}, numero:{fone}', nome_servico)
        conn.commit()
        cur_zap.close()
        salvo = True
    except Exception as e:
        print_log(f'Erro ao salva mensagem: {e}', nome_servico)
    return salvo

def altera_mensagem_local(conn, cod_mensagem, nome_servico):
    try:
        cur_fb = conn.cursor()
        sql = f"UPDATE mensagem_zap SET STATUS = 'ENVIADA' WHERE codigo = {cod_mensagem} "
        cur_fb.execute(sql)
        print_log(f'Status mensagem local alterado', nome_servico)
        conn.commit()
        cur_fb.close()
    except Exception as e:
        cur_fb.close()
        print_log(f'Não foi possivel alterar status mensagem local: {e}', nome_servico)

def config_zap(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
                SELECT ENVIAR_MENSAGEM_ANIVERSARIO,ENVIAR_MENSAGEM_PROMOCAO, 
                    ENVIAR_MENSAGEM_DIARIO, ENVIAR_MENSAGEM_LEMBRETE,MENSAGEM_ANIVERSARIO,
                    MENSAGEM_PROMOCAO,MENSAGEM_DIARIO,DIA_MENSAGEM_DIARIA, TIME_MENSAGEM_DIARIA,    
                    ULTIMO_ENVIO_ANIVERSARIO,ULTIMO_ENVIO_DIARIO,ULTIMO_ENVIO_PROMOCAO, MENSAGEM_PREAGENDAMENTO,
                    MENSAGEM_LEMBRETE, TIME_MENSAGEM_LEMBRETE
                FROM CONFIG
    """)
    colunas = [coluna[0] for coluna in cursor.description]
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    return resultados_em_dicionario[0]

def atualiza_mensagem(codigo, status):
    inicializa_conexao_mysql()

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

def retorna_pessoas_mensagemdiaria(conexao, envia_mensagem_diaria, dia_mensagem, hora_mensagem, ultimo_envio):
    pessoas_dicionario = []
    if envia_mensagem_diaria == 1:
        data_hoje = datetime.datetime.now()
        dia_semana_hoje = datetime.datetime.now().isoweekday()
        dia_semana_hoje = 0 if dia_semana_hoje == 7 else dia_semana_hoje
        hora = data_hoje.time().replace(second=0,microsecond=0)
        if ultimo_envio < data_hoje:
            if dia_mensagem == dia_semana_hoje:
                if hora_mensagem == hora:
                    try:
                        sql = "select codigo, fantasia, celular1 from pessoa p where p.celular1 <> '' and p.ativo = 'S'"
                        cursor = conexao.cursor()
                        cursor.execute(sql)
                        colunas = [coluna[0] for coluna in cursor.description]
                        pessoas = cursor.fetchall()
                        pessoas_dicionario = [dict(zip(colunas, pessoa)) for pessoa in pessoas]
                        cursor.execute('update config set ultimo_envio_diario = ?', (datetime.datetime.strftime(data_hoje, '%d.%m.%Y %H:%M:%S'),))
                        conexao.commit()
                    except Exception as e:
                        conexao.rollback()
                        print_log(f'Nao foi possivel capturar registros para mensagem diaria: {e}')
    return pessoas_dicionario

def atualiza_ano_cliente(conexao, codigo, ano):
    cursor = conexao.cursor()
    cursor.execute("""
                        UPDATE PESSOA
                        SET ANO_ENVIO_MENSAGEM_ANIVERSARIO = ?
                        WHERE CODIGO = ?;
                    """, (ano,codigo))
    # Confirmando a inserção
    conexao.commit()

def retorna_pessoas_preagendadas(conexao):
    data_hoje = datetime.datetime.now().strftime('%d.%m.%Y')
    cursor = conexao.cursor()
    cursor.execute(f"""
        SELECT a.*,p.FANTASIA, a.TELEFONE1 , s.DESCRICAO ,s.DIAS_RETORNO 
        FROM AGENDA a
        LEFT OUTER JOIN PESSOA p 
            ON a.CLIENTE  = p.CODIGO 
        LEFT OUTER JOIN SERVICOS s 
            ON a.SERVICO  = s.CODIGO 
        WHERE ENVIADOPREAGENDAMENTO IS NULL AND a.TELEFONE1 <> '' AND "DATA" BETWEEN '{data_hoje} 00:00:00' AND '{data_hoje} 23:59:59' AND status = '4'
    """)
    colunas = [coluna[0] for coluna in cursor.description]
    a = cursor.fetchall()
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in a]
    return resultados_em_dicionario

def retorna_pessoas_lembrete(conexao: fdb.Connection, tempo: datetime.time):
    data = datetime.datetime.now()
    data_formatada = data.strftime('%d.%m.%y')
    hora_agora = data.time().replace(microsecond=0)
    if hora_agora >= tempo:
        sql = f"""SELECT a.*,p.FANTASIA, a.TELEFONE1 , s.DESCRICAO
                FROM AGENDA a
                LEFT OUTER JOIN PESSOA p 
                    ON a.CLIENTE  = p.CODIGO 
                LEFT OUTER JOIN SERVICOS s 
                    ON a.SERVICO  = s.CODIGO 
                WHERE a.enviado_lembrete IS NULL
                    AND a.TELEFONE1 <> ''
                    AND status = 1
                    AND a.data_criado < '{data_formatada} 00:00:00'
                    AND A.data BETWEEN '{data_formatada} 00:00:00' AND '{data_formatada} 23:59:59'"""
        try:
            cursor = conexao.cursor()
            cursor.execute(sql)
            resultados = cursor.fetchall()
            colunas = [coluna[0] for coluna in cursor.description]
            resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in resultados]
            return resultados_em_dicionario
        except Exception as e:
            print(f'Erro ao consultar agendamentos para lembretes -> motivo: {e}')
        finally:
            if cursor:
                cursor.close()
    else:
        return []

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

def salva_retorno(codigo, retorno):
    inicializa_conexao_mysql()
    cursor = parametros.MYSQL_CONNECTION.cursor()
    cursor.execute("""
        UPDATE zap_zap
        SET retorno = %s
        WHERE CODIGO = %s;
    """, (retorno, codigo))
    parametros.MYSQL_CONNECTION.commit()

def atualiza_agenda(conexao: fdb.Connection, codigo: int, tipo: str='') -> None:
    try:
        cursor = conexao.cursor()
        if tipo.lower() == 'lembrete':
            cursor.execute("UPDATE AGENDA SET ENVIADO_LEMBRETE = 1 WHERE CODIGO = ?", (codigo,))
        elif tipo.lower() == 'pre_agendamento':
            cursor.execute("UPDATE AGENDA SET ENVIADOPREAGENDAMENTO = 1 WHERE CODIGO = ?;", (codigo,))
        else:
            print_log('Tipo de atualizacao de registro na agenda não identificado')
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print_log(f'Erro ao atualizar registro da agenda: {e}')
    finally:
        if cursor:
            cursor.close()

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
        SELECT FIRST 5 CODIGO, MENSAGEM, FONE, STATUS FROM MENSAGEM_ZAP WHERE STATUS = 'PENDENTE'
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

# Obtém o nome do arquivo do script principal (quem está chamando este código)
script_principal = os.path.basename(sys.argv[0]).replace('.py', '')

# Função que verifica se o script pode ser executado
def pode_executar(nome_script:str) -> bool:
    lock_file = nome_script + '.lock'
    caminho_lock_file = os.path.join(parametros.SCRIPT_PATH, 'temp', f'{lock_file}')
    # Verificar se o arquivo de bloqueio existe
    if os.path.exists(caminho_lock_file):
        with open(caminho_lock_file, 'r') as f:
            last_run_time_str = f.read().strip()

        try:
            # Converter a string de data e hora para um objeto datetime
            last_run_time = datetime.datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')

            # Verificar se já se passaram mais de 5 minutos desde a última execução
            if datetime.datetime.now() - last_run_time < datetime.timedelta(minutes=5):
                print_log("O script está em execução ou foi executado há menos de 5 minutos.", nome_script)
                return False
            else:
                print_log("Mais de 5 minutos se passaram, permitido executar.", nome_script)
                return True
            
        except ValueError:
            print_log("Formato de data inválido no arquivo de bloqueio, ignorando o bloqueio...", nome_script + '.txt')
            return True
    else:
        print_log("Nenhum arquivo de bloqueio encontrado, permitido executar.", nome_script + '.txt')
        return True

# Função que cria o arquivo de bloqueio
def criar_bloqueio(nome_script):
    lock_file = nome_script + '.lock'
    caminho_lock_file = os.path.join(parametros.SCRIPT_PATH, 'temp', f'{lock_file}')
    if not os.path.exists(Path(caminho_lock_file).parent):
        os.makedirs(Path(caminho_lock_file).parent)
    with open(caminho_lock_file, 'w') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Função que remove o arquivo de bloqueio
def remover_bloqueio(nome_script):
    lock_file = nome_script + '.lock'
    caminho_lock_file = os.path.join(parametros.SCRIPT_PATH, 'temp', f'{lock_file}')
    if os.path.exists(caminho_lock_file):
        os.remove(caminho_lock_file)

def crypt(action: str, src: str) -> str:
    if not src:
        return ''
    
    if isinstance(src, datetime.datetime):
        src = datetime.datetime.strftime(src, '%d/%m/%Y')

    key = 'XNGREXCAPHJKQWERTYUIOP98765LKJHASFGMNBVCAXZ13450'
    dest = ''
    key_len = len(key)
    key_pos = 0
    range_ = 128

    if action.upper() == 'C':  # Encrypt
        offset = range_
        dest = f"{offset:02X}"

        for char in src:
            src_asc = (ord(char) + offset) % 255

            if key_pos < key_len:
                key_pos += 1
            else:
                key_pos = 1

            src_asc ^= ord(key[key_pos - 1])
            dest += f"{src_asc:02X}"
            offset = src_asc

    elif action.upper() == 'D':  # Decrypt
        offset = int(src[:2], 16)
        src_pos = 2

        while src_pos < len(src):
            src_asc = int(src[src_pos:src_pos + 2], 16)

            if key_pos < key_len:
                key_pos += 1
            else:
                key_pos = 1

            tmp_src_asc = src_asc ^ ord(key[key_pos])

            if tmp_src_asc <= offset:
                tmp_src_asc = 255 + tmp_src_asc - offset
            else:
                tmp_src_asc -= offset

            dest += chr(tmp_src_asc)
            offset = src_asc
            src_pos += 2

    return dest

def verifica_dll_firebird():

    if os.path.exists('C:/Program Files/Firebird/Firebird_2_5/bin'):
        return f'{parametros.SCRIPT_PATH}\\fbclient64.dll'
    
    elif os.path.exists('C:/Program Files (x86)/Firebird/Firebird_2_5/bin/'):
        return f'{parametros.SCRIPT_PATH}/fbclient32.dll'
    
    else:
        return ''
    
def caminho_bd():
    try:
        caminho_sistema = os.path.dirname(os.path.abspath(__file__)) + '/'
        caminho_sistema = caminho_sistema.lower().replace('server','')
        caminho_ini = os.path.join(caminho_sistema, 'banco.ini')
        config = configparser.ConfigParser()
        config.read(caminho_ini)
        caminho_banco_dados = config.get('BD', 'path')
        ip_banco_dados = config.get('BD', 'ip')        
    except:
        return ''
    return caminho_banco_dados, ip_banco_dados 

def extrair_metadados_tabelas_firebird(conexao: fdb.Connection) -> dict:
    sql = """ select
                trim(rr.rdb$relation_name) as tabela,
                trim(rrf.rdb$field_name) as campo,
                case
                    when rf.rdb$computed_source is not null then 'COMPUTED BY '|| cast(rf.rdb$computed_source as varchar(500))
                    when rf.rdb$field_type = 7 then
                        case 
                            when (coalesce(rf.rdb$field_scale, 0) < 0) then
                                case rf.rdb$field_sub_type
                                    when 1 then 'NUMERIC(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    when 2 then 'DECIMAL(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    else 'UNKNOWN ' || rf.rdb$field_sub_type
                                end
                            else 'SMALLINT'
                        end
                    when rf.rdb$field_type = 8 then
                        case 
                            when (coalesce(rf.rdb$field_scale, 0) < 0) then
                                case rf.rdb$field_sub_type
                                    when 1 then 'NUMERIC(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    when 2 then 'DECIMAL(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    else 'UNKNOWN ' || rf.rdb$field_sub_type
                                end
                            else 'INTEGER'
                        end
                    when rf.rdb$field_type = 10 then 'FLOAT'
                    when rf.rdb$field_type = 12 then 'DATE'
                    when rf.rdb$field_type = 13 then 'TIME'
                    when rf.rdb$field_type = 14 then 'CHAR(' || rf.rdb$field_length || ')'
                    when rf.rdb$field_type = 16 then
                        case 
                            when (coalesce(rf.rdb$field_scale, 0) < 0) then
                                case rf.rdb$field_sub_type
                                    when 1 then 'NUMERIC(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    when 2 then 'DECIMAL(' || coalesce(rf.rdb$field_precision, 0) || ',' || abs(rf.rdb$field_scale) || ')'
                                    else 'UNKNOWN ' || rf.rdb$field_sub_type
                                end
                            else 'BIGINT'
                        end
                    when rf.rdb$field_type = 27 then 'DOUBLE PRECISION'
                    when rf.rdb$field_type = 35 then 'TIMESTAMP'
                    when rf.rdb$field_type = 37 then 'VARCHAR(' ||cast((rf.rdb$field_length / COALESCE(ch.rdb$bytes_per_character, 1)) as integer)||')'
                    when rf.rdb$field_type = 261 then
                        case rf.rdb$field_sub_type
                            when 0 then 'BLOB SUB_TYPE 0'
                            when 1 then 'BLOB SUB_TYPE 1'
                            else 'BLOB'
                        end
                    else 'UNKNOWN'
                end as tipo_campo,
                case rrf.rdb$null_flag
                    when 1 then 'NOT NULL'
                    else null
                end as NULO,
                trim(replace(upper(cast(rrf.rdb$default_source as varchar(500))), 'DEFAULT', '')) as valor_padrao,
                cast(rrf.rdb$description as varchar(500)) as descricao_campo,
                trim(ch.rdb$character_set_name) as charset,
                trim(rc.rdb$collation_name) as collation
            from
                rdb$relations rr
            left outer join
                rdb$relation_fields rrf on rrf.rdb$relation_name = rr.rdb$relation_name
            left outer join 
                rdb$fields rf on rf.rdb$field_name = rrf.rdb$field_source
            left outer join
                rdb$character_sets ch on ch.rdb$character_set_id = rf.rdb$character_set_id
            left outer join
                rdb$collations rc ON rc.rdb$collation_id = rf.rdb$collation_id AND rc.rdb$character_set_id = rf.rdb$character_set_id
            where
                rr.rdb$system_flag = 0
            order by
                rr.rdb$relation_name,
                rrf.rdb$field_position """
    
    metadados = {}
    try:
        cursor: fdb.Cursor = conexao.cursor()
        cursor.execute(sql)
        resultados = cursor.fetchall()
        for linha in resultados:
            tabela = linha[0]
            campo = linha[1]
            tipo_campo = linha[2]
            nulo = linha[3]
            valor_padrao = linha[4]
            descricao_campo = linha[5]
            charset = linha[6]
            collation = linha[7]

            if not tabela in metadados:
                metadados[tabela] = {}
            metadados[tabela][campo] = {
                                        'TIPO': tipo_campo,
                                        'NULO': nulo,
                                        'VALOR_PADRAO': valor_padrao,
                                        'DESCRICAO': descricao_campo,
                                        'CHARSET': charset,
                                        'COLLATION': collation
                                        }
    except Exception as e:
        print_log(f'Nao foi possível extrair metadados do banco -> motivo: {e}')
    finally:
        cursor.close()

    return metadados

def extrair_metadados_chaves_primarias_firebird(conexao: fdb.Connection) -> dict:
    select_sql = ''' SELECT 
                    trim(RC.RDB$RELATION_NAME) AS TABELA,
                    trim(IDX.RDB$INDEX_NAME) AS INDICE,
                    trim(SEG.RDB$FIELD_NAME) AS COLUNA
                FROM RDB$RELATION_CONSTRAINTS RC
                JOIN RDB$INDEX_SEGMENTS SEG ON RC.RDB$INDEX_NAME = SEG.RDB$INDEX_NAME
                JOIN RDB$INDICES IDX ON RC.RDB$INDEX_NAME = IDX.RDB$INDEX_NAME
                WHERE RC.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
                ORDER BY RC.RDB$RELATION_NAME'''
    metadados = {}
    try:
        cusor: fdb.Cursor = conexao.cursor()
        cusor.execute(select_sql)
        resultados = cusor.fetchall()

        for linha in resultados:
            tabela = linha[0]
            indice = linha[1]
            campo = linha[2]

            if tabela not in metadados:
                metadados[tabela] = {}
            
            if indice not in metadados[tabela]:
                metadados[tabela][indice] = []
            
            metadados[tabela][indice].append(campo)

    except Exception as e:
        print_log(f'Nao foi possivel extrair metadados das chaves -> motivo: {e}')
    finally:
        if cusor:
            cusor.close()
    
    return metadados

def extrair_metadados_chaves_estrangeiras(conexao: fdb.Connection) -> dict:
    select_sql = ''' SELECT
                        trim(rc.RDB$RELATION_NAME) AS tabela,
                        trim(ixs.RDB$FIELD_NAME) AS campo,
                        trim(rc.rdb$constraint_name) as chave_estrangeira,
                        CASE
                            WHEN (
                                SELECT FIRST 1 rel.RDB$RELATION_NAME
                                FROM RDB$RELATION_CONSTRAINTS rel
                                WHERE rel.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
                                AND rel.RDB$INDEX_NAME = refc.RDB$CONST_NAME_UQ
                            ) IS NULL
                            THEN (
                                SELECT trim(rel.RDB$RELATION_NAME)
                                FROM RDB$RELATION_CONSTRAINTS rel
                                WHERE rel.RDB$CONSTRAINT_NAME = refc.RDB$CONST_NAME_UQ
                            )
                            ELSE (
                                SELECT FIRST 1 trim(rel.RDB$RELATION_NAME)
                                FROM RDB$RELATION_CONSTRAINTS rel
                                WHERE rel.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
                                AND rel.RDB$INDEX_NAME = refc.RDB$CONST_NAME_UQ
                            )
                        END AS tabela_referenciada,
                        CASE
                            WHEN (
                                SELECT FIRST 1 trim(ixs2.RDB$FIELD_NAME)
                                FROM RDB$INDEX_SEGMENTS ixs2
                                WHERE ixs2.RDB$INDEX_NAME = refc.RDB$CONST_NAME_UQ
                            ) IS NULL
                            THEN (
                                SELECT FIRST 1 trim(ix2.RDB$FIELD_NAME)
                                FROM RDB$INDEX_SEGMENTS ix2
                                WHERE ix2.RDB$INDEX_NAME = (
                                    SELECT rrc2.RDB$INDEX_NAME
                                    FROM RDB$RELATION_CONSTRAINTS rrc2
                                    WHERE rrc2.RDB$CONSTRAINT_NAME = refc.RDB$CONST_NAME_UQ
                                )
                            )
                            ELSE (
                                SELECT FIRST 1 trim(ixs2.RDB$FIELD_NAME)
                                FROM RDB$INDEX_SEGMENTS ixs2
                                WHERE ixs2.RDB$INDEX_NAME = refc.RDB$CONST_NAME_UQ
                            )
                        END AS campo_referenciado,
                        trim(refc.RDB$UPDATE_RULE) AS regra_update,
                        trim(refc.RDB$DELETE_RULE) AS regra_delete
                    FROM RDB$RELATION_CONSTRAINTS rc
                    JOIN RDB$REF_CONSTRAINTS refc ON rc.RDB$CONSTRAINT_NAME = refc.RDB$CONSTRAINT_NAME
                    JOIN RDB$INDEX_SEGMENTS ixs ON rc.RDB$INDEX_NAME = ixs.RDB$INDEX_NAME
                    WHERE rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
                    ORDER BY rc.RDB$RELATION_NAME, rc.RDB$CONSTRAINT_NAME'''
    
    metadados = {}
    try:
        cusor: fdb.Cursor = conexao.cursor()
        cusor.execute(select_sql)
        resultados = cusor.fetchall()
        
        for resultado in resultados:
            tabela = resultado[0]
            campo = resultado[1]
            nome_chave = resultado[2]
            tabela_referenciada = resultado[3]
            campo_referenciado = resultado[4]
            regra_update = resultado[5]
            regra_delete = resultado[6]

            if tabela not in metadados:
                metadados[tabela] = {}

            metadados[tabela][nome_chave] = {
                'CAMPO': campo,
                'TABELA_REFERENCIADA': tabela_referenciada,
                'CAMPO_REFERENCIADO': campo_referenciado,
                'REGRA_UPDATE': regra_update,
                'REGRA_DELETE': regra_delete
            }
    except Exception as e:
        print_log(f'Nao foi possivel extrair informacoes das chaves estrangeiras -> motivo: {e}')
    finally:
        if cusor:
            cusor.close()
    
    return metadados

def extrair_metadados_procedures(conexao: fdb.Connection) -> dict:
    select_sql = ''' select
                        trim(rp.rdb$procedure_name) as nome_procedure,
                        cast(rp.rdb$procedure_source as varchar(20000)) as procedimento
                    from
                        rdb$procedures rp
                    where
                        rp.rdb$system_flag = 0'''
    metadados = {}
    try:
        cursor: fdb.Cursor = conexao.cursor()
        cursor.execute(select_sql)
        resultados = cursor.fetchall()

        for resultado in resultados:
            procedure = resultado[0]
            conteudo_procedure = resultado[1]
            metadados[procedure] = {'PROCEDIMENTO': conteudo_procedure}

    except Exception as e:
        print_log(f'Nao foi possivel extrair informacoes das procedures -> motivo: {e}')
    finally:
        if cursor:
            cursor.close()
    
    return metadados

def extrair_metadados_triggers(conexao: fdb.Connection) -> dict:
    # select_sql = '''select
    #                     trim(rt.rdb$relation_name) as tabela,
    #                     trim(rt.rdb$trigger_name) as nome_trigger,
    #                     cast(rt.rdb$trigger_source as varchar(20000)) as conteudo,
    #                     trim(rt.rdb$trigger_inactive) as trigger_inativa
    #                 from
    #                     rdb$triggers rt
    #                 where
    #                     rt.rdb$system_flag = 0
    #                 order by
    #                     rt.rdb$relation_name, rt.rdb$trigger_sequence'''
    select_sql = """SELECT
                        TRIM(rt.rdb$relation_name) AS tabela,
                        TRIM(rt.rdb$trigger_name) AS nome_trigger,                       
                        CASE TRIM(rt.rdb$trigger_type)
                            WHEN 1 THEN 'BEFORE INSERT'
                            WHEN 2 THEN 'AFTER INSERT'
                            WHEN 3 THEN 'BEFORE UPDATE'
                            WHEN 4 THEN 'AFTER UPDATE'
                            WHEN 5 THEN 'BEFORE DELETE'
                            WHEN 6 THEN 'AFTER DELETE'
                            WHEN 17 THEN 'BEFORE INSERT OR UPDATE'
                            WHEN 18 THEN 'AFTER INSERT OR UPDATE'
                            WHEN 25 THEN 'BEFORE INSERT OR DELETE'
                            WHEN 26 THEN 'AFTER INSERT OR DELETE'
                            WHEN 27 THEN 'BEFORE UPDATE OR DELETE'
                            WHEN 28 THEN 'AFTER UPDATE OR DELETE'
                            WHEN 113 THEN 'BEFORE INSERT OR UPDATE OR DELETE'
                            WHEN 114 THEN 'AFTER INSERT OR UPDATE OR DELETE'
                            ELSE 'DESCONHECIDO'
                        END AS tipo_descricao,
                        CAST(rt.rdb$trigger_source AS VARCHAR(20000)) AS conteudo,
                        TRIM(rt.rdb$trigger_inactive) AS trigger_inativa
                    FROM
                        rdb$triggers rt
                    WHERE
                        rt.rdb$system_flag = 0
                    ORDER BY
                        rt.rdb$relation_name, rt.rdb$trigger_sequence;"""
    metadados = {}
    try:
        cursor: fdb.Cursor = conexao.cursor()
        cursor.execute(select_sql)
        resultados = cursor.fetchall()

        for resultado in resultados:
            tabela = resultado[0]
            nome_trigger = resultado[1]
            tipo = resultado[2]
            conteudo_trigger = resultado[3]
            trigger_inativa = resultado[4]

            if tabela not in metadados:
                metadados[tabela] = {}

            metadados[tabela][nome_trigger] = {
                'TIPO': tipo,
                'CONTEUDO': conteudo_trigger,
                'INATIVA': trigger_inativa
            }

    except Exception as e:
        print_log(f'Nao foi possivel extrair informacoes das triggers -> motivo: {e}')
    finally:
        if cursor:
            cursor.close()
    
    return metadados

def obter_nome_terminal():
    import socket
    return socket.gethostname()

def configurar_pos_printer(modulo):
    nome_terminal = obter_nome_terminal()
    nome_terminal = nome_terminal.upper()


    resultado_impressora = selectfb(f"""
        SELECT I.PORTA_IMPRESSORA
        FROM IMPRESSORAS_PADROES IP
        LEFT JOIN IMPRESSORA I ON IP.CODIGO_IMPRESSORA = I.CODIGO
        WHERE MODULO = '{modulo}' AND IP.NOME_TERMINAL = '{nome_terminal}'
    """)

    row = resultado_impressora[0]

    return row[0]


#====================================== funcoes replicador ====================================

def buscar_elemento_mysql(tabela: str, codigo: int, cnpj: str ='', codigo_global = None, nome_servico:str = 'replicador') -> Optional[dict]:
    try:
        
        cursor = parametros.MYSQL_CONNECTION_REPLICADOR.cursor(dictionary=True)
        if codigo_global:
            sql_select = f"SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = %s"
            cursor.execute(sql_select, (codigo_global,))
        else:
            chave_primaria = buscar_nome_chave_primaria(tabela)
            if not chave_primaria:
                print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                return None
            
            sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = %s AND CNPJ_EMPRESA = %s"
            cursor.execute(sql_select, (codigo, cnpj))

        dados = cursor.fetchone()

        if dados == None:
            print_log(f'Não há elemento que possua esta chave no Mysql - chave: {codigo} ou este código global: {codigo_global}', nome_servico)
            return None
        
        dados = dict(dados)
        dados.pop('CNPJ_EMPRESA')

        cursor.close()

        return dados
    except Exception as e:
        print_log(f"Erro ao buscar elemento MySQL: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()

def buscar_elemento_firebird(tabela:str, codigo:int, codigo_global: int = 0, nome_servico:str = 'replicador') -> Optional[dict]:
    try:
        cursor = parametros.FIREBIRD_CONNECTION.cursor()

        if codigo_global:
            sql_select = f'SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = {codigo_global}'
            cursor.execute(sql_select)
            dados = cursor.fetchone()

            if not dados:
                chave_primaria = buscar_nome_chave_primaria(tabela)
                if not chave_primaria:
                    print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                    return None
                
                if not codigo:
                    return None

                sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{codigo}'"
                cursor.execute(sql_select)
                dados = cursor.fetchone()
        else:
            chave_primaria = buscar_nome_chave_primaria(tabela)

            if not chave_primaria:
                print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                return None
            
            sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{codigo}'"

            cursor.execute(sql_select)

            dados = cursor.fetchone()

        if dados:
            colunas = [desc[0] for desc in cursor.description]
            dados = dict(zip(colunas, dados))
        else:
            print_log(f'Não há elemento Firebird com esta chave - chave: {codigo} (pode ter sido excluido ou precisa ser adicionado!)', nome_servico)

        return dados

    except Exception as e:
        print_log(f"Erro ao buscar elemento no Firebird: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()

def verifica_empresa_firebird(tabela:str, dados: dict, nome_servico:str = 'replicador') -> Optional[tuple[int, str]]:
    cursor = parametros.FIREBIRD_CONNECTION.cursor()
    codigo_empresa = 0
    if tabela == 'EMPRESA':
        codigo_empresa = dados['CODIGO']
    else:
        for coluna, valor in dados.items():
            if 'EMPRESA' in coluna.upper():
                if isinstance(valor, int):
                    codigo_empresa = valor
                    break
            elif 'EMITENTE' in coluna.upper():
                if isinstance(valor, int):
                    codigo_empresa = valor
                    break
    cnpj = ''
    if codigo_empresa > 0:
        try:
            cursor.execute(f'SELECT CNPJ FROM EMPRESA WHERE CODIGO = {codigo_empresa}')
            cnpj = cursor.fetchall()[0][0]
        except Exception as e:
            print_log(f'Nao foi possivel consultar empresa: {e}', nome_servico)

    return codigo_empresa, cnpj

def buscar_nome_chave_primaria(tabela: str, nome_servico:str = 'replicador') -> str|None:
    try:
        cursor = parametros.FIREBIRD_CONNECTION.cursor()

        query_codigo = f"""
        SELECT TRIM(RDB$FIELD_NAME)
        FROM RDB$RELATION_FIELDS
        WHERE RDB$RELATION_NAME = '{tabela}' AND UPPER(RDB$FIELD_NAME) = 'CODIGO'
        """
        cursor.execute(query_codigo)
        row_codigo = cursor.fetchone()
        
        if row_codigo:
            return 'CODIGO' 
        
        # Verificar se há uma chave primária
        query = f"""
        SELECT TRIM(segments.RDB$FIELD_NAME)
        FROM RDB$RELATION_CONSTRAINTS constraints
        JOIN RDB$INDEX_SEGMENTS segments ON constraints.RDB$INDEX_NAME = segments.RDB$INDEX_NAME
        WHERE constraints.RDB$RELATION_NAME = '{tabela}'
          AND constraints.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
        """
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            return row[0]  # Retorna o nome da coluna da chave primária
         
        
        # Se não encontrar chave primária nem campo 'codigo', retornar None
        return None
        
    except Exception as e:
        print_log(f"Erro ao buscar nome da chave primária no Firebird: {e}", nome_servico)
        return None


def verifica_valor_chave_primaria(tabela:str, codigo_global:str, chave_primaria:str) -> str | None:
    elemento = buscar_elemento_firebird(tabela, None, codigo_global)
    return elemento.get(chave_primaria, None)


def consulta_cnpjs_local() -> list | None:
    try:
        cursor = parametros.FIREBIRD_CONNECTION.cursor()
        cursor.execute('SELECT CODIGO, CNPJ FROM EMPRESA')
        empresas = cursor.fetchall()
        cursor.close()
        if not empresas:
            return None
        return empresas
    except Exception as e:
        print_log(f'Erro ao consultar os cnpjs locais -> motivo: {e}')

def tratar_valores(dados: dict) -> list:
    valores = []
    for key, valor in dados.items():
        if isinstance(valor, fdb.fbcore.BlobReader):  # Verifica se o valor é BLOB
            blob = valor.read()
            valores.append(blob)
            valor.close()

        elif isinstance(valor, datetime.timedelta): # Converte tempo de segundos para hora : minuto : segundo
            total_de_segundos = valor.total_seconds()
            horas = int(total_de_segundos // 3600)
            segundos_restantes = total_de_segundos % 3600
            minutos = int(segundos_restantes // 60)
            segundos_restantes = segundos_restantes % 60
            valor = datetime.time(hour=horas, minute=minutos, second=int(segundos_restantes))
            valores.append(valor)

        else:
            valores.append(valor)  # Adiciona os outros valores
    return valores

def delete_registro_replicador(tabela:str, acao:str, chave:str, codigo_global:str = 0, firebird:bool=True, nome_servico:str='replicador') -> None:

    if firebird:
        try:
            connection = parametros.FIREBIRD_CONNECTION
            sql_delete = "DELETE FROM REPLICADOR WHERE chave = ? AND tabela = ? AND acao = ? ROWS 1;"
            cursor = connection.cursor()
            cursor.execute(sql_delete, (chave, tabela, acao,))

            connection.commit()
        except fdb.fbcore.DatabaseError as e:
            print_log(f"Erro ao deletar registros da tabela REPLICADOR: {e}", nome_servico)
            connection.rollback()
        finally:
            if cursor:
                cursor.close()
    else:
        try:
            connection = parametros.MYSQL_CONNECTION_REPLICADOR
            if codigo_global:
                sql_delete = "DELETE FROM REPLICADOR WHERE TABELA = %s AND ACAO = %s AND CODIGO_GLOBAL = %s LIMIT 1;"
                valores = tabela, acao, codigo_global
            else:
                sql_delete = "DELETE FROM REPLICADOR WHERE CHAVE = %s AND TABELA = %s AND ACAO = %s LIMIT 1;"
                valores = chave, tabela, acao

            cursor = connection.cursor()
            cursor.execute(sql_delete, valores)

            connection.commit()
        except Exception as e:
            print_log(f"Erro ao deletar registros da tabela REPLICADOR: {e}", nome_servico)
        finally:
            if cursor:
                cursor.close()