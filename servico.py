import os
import datetime
import logging
import json
from logging.handlers import RotatingFileHandler
import requests
import urllib.request
import time
import subprocess
import fdb
import psutil
import threading
import mysql.connector
import parametros
from funcoes import print_log, exibe_alerta, inicializa_conexao_mysql, carregar_configuracoes, atualizar_conexoes_firebird

_svc_name_ = "MaxServices"
_svc_display_name_ = "MaxServices"
_svc_description_ = "Monitora uso de sistema e dados"
MAXUPDATE = 'MaxUpdate'
SCRIPT_URL = 'https://maxsuport.com.br/static/update/MaxUpdate.py'
SERVICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MaxUpdate.py')

def MaxServices():
    try:
        inicializa_conexao_mysql()
        carregar_configuracoes()

        try:
            print_log('Verificando atualizações...')
            versao_online = verifica_versao_online()
            versao_local = verifica_versao_local()

            if versao_online > versao_local:
                atualiza_script(versao_online)
                
            verifica_dados_local()

            print_log('Agora vou dormir 10 segundos')

        except Exception as e:
            print_log(f'Erro no loop principal: {e}')
    except Exception as e:
        print_log(f'Erro durante a inicialização: {e}')

def verifica_versao_online():
    try:
        url = "https://maxsuport.com.br/static/update/versaoupdate.txt"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return int(response.text)
        else:
            print_log(f"Erro ao obter o conteúdo da página: {response.status_code}")
            return 0
    except Exception as e:
        print_log(f'Erro ao verificar versão online: {e}')
        return 0

def verifica_versao_local():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'versaoupdate.txt'), 'r') as arquivo:
            return int(arquivo.read())
    except:
        print_log('Arquivo da versão local não encontrado')
        return 0

def atualiza_script( versao_online):

    try:
        urllib.request.urlretrieve(SCRIPT_URL, SERVICE_PATH)
        print_log('Download efetuado')

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'versaoupdate.txt'), 'w') as arquivo:
            arquivo.write(str(versao_online))

        print_log('Versão atualizada salva')
    except Exception as e:
        print_log(f'Erro ao atualizar script: {e}')

def verifica_dados_local():
    try:
        print_log("Pegando dados locais - MaxServices")
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo']
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil'].replace('\\', '/')
            caminho_base_dados_gfil = caminho_base_dados_gfil.split('/')[0] + '/' + caminho_base_dados_gfil.split('/')[1]

            print_log(f"Local valor {ativo} do CNPJ {cnpj} - MaxServices")

            if ativo == "0" and sistema_em_uso == "2":
                print_log("Encerra Processo do GFIL - MaxServices")
                for proc in psutil.process_iter(['name', 'exe']):
                    if 'FIL' in proc.info['name']:
                        if caminho_base_dados_gfil in proc.info['exe'].replace('\\', '/'):
                            print_log(f"Encerra Processo do GFIL na proc {caminho_base_dados_gfil}, no caminho {proc.info['exe']} - MaxServices")
                            proc.kill()
                            print_log("Iniciar conexão com alerta - MaxServices")
                            exibe_alerta()

            if sistema_em_uso == "1":
                data_cripto = '80E854C4A6929988F97AE2'
                if ativo == "1":
                    data_cripto = '80E854C4A6929988F879E1'
                try:
                    con = parametros.FIREBIRD_CONNECTION
                    cur = con.cursor()
                    comando = 'Liberar' if ativo == "1" else 'Bloquear'
                    print_log(f"Comando para {comando} maxsuport - MaxServices")
                    cur.execute(f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}'")
                    con.commit()
                except fdb.fbcore.DatabaseError as e:
                    print_log(f"Erro ao executar consulta: {e}")
    
    except Exception as e:
        print_log(f"Erro: {_svc_name_} {e} - MaxServices")
