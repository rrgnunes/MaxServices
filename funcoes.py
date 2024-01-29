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

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'


def print_log(texto):
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