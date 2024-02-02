import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import threading
import time
from parametros import *
import mysql.connector
import json
import subprocess
import lzma
from ftplib import FTP
import glob
import socket
import zlib
import fdb
import psutil
import inspect


# Variáveis globais para os parâmetros do banco de dados
DB_HOST = HOSTMYSQL
DB_USER = USERMYSQL
DB_PASSWORD = PASSMYSQL
DB_DATABASE = BASEMYSQL

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
# Configuração do logger
# chamador = inspect.currentframe().f_back
# nome = os.path.basename(chamador.f_code.co_filename)
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
# Configuração do handler
log_file = SCRIPT_PATH + 'log.log'
max_bytes = 1024 * 1024  # 1 MB
backup_count = 3  # Número de arquivos de backup a serem mantidos
handler = RotatingFileHandler(
    log_file, maxBytes=max_bytes, backupCount=backup_count)
handler.setLevel(logging.DEBUG)

# Formatação do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Adicionando o handler ao logger
logger.addHandler(handler) 

def print_log(texto):
       
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')

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

        print("Inserção bem-sucedida!")

    except Exception as e:
        print(f"Erro durante a inserção: {e}")

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

        print("Exclusão bem-sucedida!")

    except Exception as e:
        print(f"Erro durante a exclusão: {e}")

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

        print("Atualização bem-sucedida!")

    except Exception as e:
        print(f"Erro durante a atualização: {e}")

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
            print("Nenhum resultado encontrado.")
            return []

    except Exception as e:
        print(f"Erro durante a consulta: {e}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()            
