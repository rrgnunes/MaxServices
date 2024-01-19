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

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'

# Configuração do logger
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


def exibe_alerta(aviso):
    # Envia Alerta
    # Configurar as informações do servidor
    host = 'localhost'  # Endereço IP ou nome do host do servidor
    port = 15001  # Porta do servidor

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


def print_log(texto):
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')