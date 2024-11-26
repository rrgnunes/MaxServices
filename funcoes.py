import datetime
import os
import mysql.connector
from mysql.connector import Error
import inspect
import xml.etree.ElementTree as ET
import sys
import fdb
import parametros
import psutil as ps
from pathlib import Path
from decimal import Decimal
import subprocess
from funcoes_zap import *

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
        if parametros.MYSQL_CONNECTION == None or not parametros.MYSQL_CONNECTION.is_connected():
            parametros.MYSQL_CONNECTION = mysql.connector.connect(
                host=parametros.HOSTMYSQL,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=parametros.BASEMYSQL,
                auth_plugin='mysql_native_password'  # Força o uso do plugin correto
            )
        print_log("Conexão com MySQL estabelecida com sucesso.")
    except mysql.connector.Error as err:
        print_log(f"Erro ao conectar ao MySQL: {err}")

   

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

def inicializa_conexao_mysql_replicador(database):
    try:
        if parametros.MYSQL_CONNECTION_REPLICADOR == None:
            parametros.MYSQL_CONNECTION_REPLICADOR = mysql.connector.connect(
                host=parametros.HOSTMYSQL,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=database
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
    for row in cursor.fetchall():
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
                    if tipo in ('INTEGER', 'NUMERIC', 'DECIMAL', 'FLOAT', 'SMALLINT', 'DATE', 'TIME', 'DOUBLE', 'TIMESTAMP'):
                        if tipo in ('INTEGER', 'SMALLINT', 'DATE', 'TIME', 'TIMESTAMP'):
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
    status = 'PENDENTE'
    cursor = parametros.MYSQL_CONNECTION.cursor()
    cursor.execute("""
        UPDATE zap_zap
        SET STATUS = %s,
            DATAHORA_ENVIADO = %s
        WHERE CODIGO = %s;
    """, (status,data_str + ' ' + hora_str, codigo))
    parametros.MYSQL_CONNECTION.commit()

def numerador(conexao, tabela, campo, filtra, where, valor):
    resultado = 0
    cursor = conexao.cursor()
    if filtra == 'N':
        cursor.execute(f"SELECT MAX({campo}) AS MAIOR FROM {tabela}")
    elif filtra == 'S':
        cursor.execute(f"SELECT MAX({campo}) AS MAIOR FROM {tabela} WHERE {where} = {valor}")
    # Obtém os nomes das colunas
    colunas = [coluna[0] for coluna in cursor.description]
    # Constrói uma lista de dicionários, onde cada dicionário representa uma linha
    resultados_em_dicionario = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    if resultados_em_dicionario != None:
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

# Nome do arquivo de bloqueio com o nome do script principal
LOCK_FILE = f'/tmp/{script_principal}.lock'
# Função que verifica se o script pode ser executado
def pode_executar(nome_script:str) -> bool:
    lock_file = nome_script + '.lock'
    # Verificar se o arquivo de bloqueio existe
    if os.path.exists(lock_file):
        with open(lock_file, 'r') as f:
            last_run_time_str = f.read().strip()

        try:
            # Converter a string de data e hora para um objeto datetime
            last_run_time = datetime.datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')

            # Verificar se já se passaram mais de 5 minutos desde a última execução
            if datetime.datetime.now() - last_run_time < datetime.timedelta(minutes=5):
                print_log("O script está em execução ou foi executado há menos de 5 minutos.", nome_script + '.txt')
                return False
            else:
                print_log("Mais de 5 minutos se passaram, verificando se script ja esta em execução", nome_script + '.txt')
                executar = True
                # Verifica se o script ja esta em execução
                for proc in ps.process_iter():
                    if proc.as_dict()['name'] == 'python.exe':
                        if nome_script in proc.as_dict()['cmdline'][1]:
                            executar = False
                            print_log('Script ja esta em execução, não pode ser executado novamente', nome_script + '.txt')
                            break
                return executar

        except ValueError:
            print_log("Formato de data inválido no arquivo de bloqueio, ignorando o bloqueio...", nome_script + '.txt')
            return True
    else:
        print_log("Nenhum arquivo de bloqueio encontrado, permitido executar.", nome_script + '.txt')
        return True

# Função que cria o arquivo de bloqueio
def criar_bloqueio(nome_script):
    lock_file = nome_script + '.lock'
    with open(lock_file, 'w') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Função que remove o arquivo de bloqueio
def remover_bloqueio(nome_script):
    lock_file = nome_script + '.lock'
    if os.path.exists(lock_file):
        os.remove(lock_file)
