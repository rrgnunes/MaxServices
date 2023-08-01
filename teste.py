import win32serviceutil
import win32service
import time
import mysql.connector
import os
import psutil
import threading
import logging
import socket
import subprocess
import psutil
import json
import datetime
import lzma
import glob
import fdb
import zlib
from ftplib import FTP
import logging
from logging.handlers import RotatingFileHandler


def print_log(texto):
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    # logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')


# Conexão com o banco de dados
try:
    print_log(f"pega dados local - xmlcontador")
    if os.path.exists("C:/Users/Public/config.json"):
        with open('C:/Users/Public/config.json', 'r') as config_file:
            config = json.load(config_file)
        for cnpj in config['sistema']:
            parametros = config['sistema'][cnpj]
            ativo = parametros['sistema_ativo'] == '1'
            sistema_em_uso = parametros['sistema_em_uso_id']
            pasta_compartilhada_backup = parametros['pasta_compartilhada_backup']
            caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
            caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
            porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
            caminho_base_dados_gfil = parametros['caminho_base_dados_gfil']
            caminho_gbak_firebird_gfil = parametros['caminho_gbak_firebird_gfil']
            porta_firebird_gfil = parametros['porta_firebird_gfil']
            data_hora = datetime.datetime.now()
            data_hora_formatada = data_hora.strftime(
                '%Y_%m_%d_%H_%M_%S')
            timer_minutos_backup = parametros['timer_minutos_backup']

            if ativo:
                conn = mysql.connector.connect(
                    host="177.153.69.3",
                    user="dinheiro",
                    password="MT49T3.6%B",
                    database="maxservices"
                )

                print_log(f"Inicia select das notas - xmlcontador")
                if sistema_em_uso == '1':  # maxsuport
                    if pasta_compartilhada_backup != '' and \
                            caminho_base_dados_maxsuport != '' and \
                            caminho_gbak_firebird_maxsuport != '' and \
                            porta_firebird_maxsuport != '':

                        con = fdb.connect(
                            host='localhost',
                            database=caminho_base_dados_maxsuport,
                            user='sysdba',
                            password='masterkey',
                            port=porta_firebird_maxsuport
                        )

                        cur = con.cursor()
                        cur.execute(
                            'select n.numero,n.chave,n.data_emissao,n.fkempresa, n.xml, n.situacao from nfe_master n')
                        rows = cur.fetchall()
                        for row in rows:
                            print(row)

                elif sistema_em_uso == '2':  # gfil
                    if pasta_compartilhada_backup != '' and \
                            caminho_base_dados_gfil != '' and \
                            caminho_gbak_firebird_gfil != '':
                        con = fdb.connect(
                            host='localhost',
                            database=caminho_base_dados_gfil,
                            user='GFILMASTER',
                            password='b32@m451',
                            port=porta_firebird_gfil
                        )

                        cur = con.cursor()
                        cur.execute('''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as cnpj_empresa 
                                        FROM CONTABILISTA c 
                                            LEFT OUTER JOIN DIVERSOS d 
                                            ON c.FILIAL  = d.FILIAL ''')
                        rows = cur.fetchall()
                        rows_dict = [
                            dict(zip([column[0] for column in cur.description], row)) for row in rows]

                        for row in rows_dict:
                            XML = zlib.decompress(row[1])
                            XML_CANCELAM = zlib.decompress(row[2])
                            print(XML)
                            print(XML_CANCELAM)

                        cur = con.cursor()
                        # cur.execute('SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND (rdb$system_flag IS NULL OR rdb$system_flag = 0)')
                        cur.execute(
                            'select first 1 DATA_EMIS_NFE,XML,XML_CANCELAM from nfe_mestre n WHERE n.DATA_EMIS_NFE > dateadd(DAY,-5,CURRENT_DATE)')
                        rows = cur.fetchall()
                        for row in rows:
                            XML = zlib.decompress(row[1])
                            XML_CANCELAM = zlib.decompress(row[2])
                            print(XML)
                            print(XML_CANCELAM)

except Exception as a:
    # self.logger.error(f"{self._svc_name_} {a}.")
    print(a)
