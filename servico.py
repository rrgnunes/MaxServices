import win32serviceutil
import win32service
import servicemanager
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
from parametros import HOSTMYSQL, USERMYSQL, PASSMYSQL, BASEMYSQL, USERFB, PASSFB, HOSTFB, DATABASEFB, PORTFB, MYSQL_CONNECTION, FIREBIRD_CONNECTION, CNPJ_CONFIG
from funcoes import  print_log, exibe_alerta,inicializa_conexao_mysql,carregar_configuracoes,atualizar_conexoes_firebird

class MaxServices(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaxServices"
    _svc_display_name_ = "MaxServices"
    _svc_description_ = "Monitora uso de sistema e dados"
    MAXUPDATE = 'MaxUpdate'
    SCRIPT_URL = 'https://maxsuport.com.br/static/update/MaxUpdate.py'
    SERVICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MaxUpdate.py')

    def __init__(self, args):
        super().__init__(args)
        self.stop = False
        self.threads = []

        inicializa_conexao_mysql()
        carregar_configuracoes()
        atualizar_conexoes_firebird()

        # Adiciona cada thread na lista de threads
        self.add_thread('thread_verifica_remoto', 'ThreadVerificaRemoto')
        self.add_thread('thread_backup_local', 'ThreadBackupLocal')
        self.add_thread('thread_servidor_socket', 'ThreadServidorSocket')
        self.add_thread('thread_xml_contador', 'ThreadXmlContador')
        self.add_thread('thread_atualiza_banco', 'ThreadAtualizaBanco')
        self.add_thread('thread_zap_automato', 'ThreadZapAutomato')
        self.add_thread('thread_IBPT_NCM_CEST', 'ThreadIBPTNCMCEST')

    def add_thread(self, module_name, class_name):
        try:
            module = __import__(module_name)
            thread_class = getattr(module, class_name)
            self.threads.append(thread_class())
            print_log(f'Thread {class_name} carregada com sucesso.')
        except Exception as e:
            print_log(f'Erro ao carregar {class_name}: {e}')

    def SvcStop(self):
        try:
            for thread in self.threads:
                thread.event.set()
        except Exception as e:
            print_log(f'Erro ao parar as threads: {e}')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop = True
        if MYSQL_CONNECTION is not None:
            MYSQL_CONNECTION.close()
            print_log("Conexão com MySQL encerrada.")
        if FIREBIRD_CONNECTION is not None:
            FIREBIRD_CONNECTION.close()
            print_log("Conexão com Firebird encerrada.")

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        while not self.stop_event.wait(10):  # Aguarda 10 segundos ou até que o evento seja sinalizado
            try:
                print_log('Verificando atualizações...')
                versao_online = self.verifica_versao_online()
                versao_local = self.verifica_versao_local()

                if versao_online > versao_local:
                    self.atualiza_script(versao_online)
                else:
                    self.verifica_e_inicia_servico()

                for thread in self.threads:
                    self.start_thread_safe(thread)
                    
                self.verifica_dados_local()

                print_log('Agora vou dormir 10 segundos')

                carregar_configuracoes()
                atualizar_conexoes_firebird()
            except Exception as e:
                print_log(f'Erro no loop principal: {e}')

    def verifica_versao_online(self):
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

    def verifica_versao_local(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'versaoupdate.txt'), 'r') as arquivo:
                return int(arquivo.read())
        except:
            print_log('Arquivo da versão local não encontrado')
            return 0

    def atualiza_script(self, versao_online):
        try:
            win32serviceutil.StopService(self.MAXUPDATE)
            print_log('Serviço parado')
        except:
            print_log('Serviço não encontrado')

        try:
            win32serviceutil.RemoveService(self.MAXUPDATE)
            print_log('Serviço removido')
        except:
            print_log('Serviço não removido')

        try:
            urllib.request.urlretrieve(self.SCRIPT_URL, self.SERVICE_PATH)
            print_log('Download efetuado')

            subprocess.call(f'python "{self.SERVICE_PATH}" install', shell=True)
            print_log('Serviço instalado')

            subprocess.call(f'python "{self.SERVICE_PATH}" start', shell=True)
            print_log('Serviço iniciado')

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'versaoupdate.txt'), 'w') as arquivo:
                arquivo.write(str(versao_online))

            print_log('Versão atualizada salva')
        except Exception as e:
            print_log(f'Erro ao atualizar script: {e}')

    def verifica_e_inicia_servico(self):
        try:
            service_status = win32serviceutil.QueryServiceStatus(self.MAXUPDATE)[1]
            if service_status != win32service.SERVICE_RUNNING:
                subprocess.call(f'python "{self.SERVICE_PATH}" start', shell=True)
                print_log('Serviço iniciado')
        except:
            subprocess.call(f'python "{self.SERVICE_PATH}" install', shell=True)
            print_log('Serviço instalado')
            subprocess.call(f'python "{self.SERVICE_PATH}" start', shell=True)
            print_log('Serviço iniciado')

    def start_thread_safe(self, thread):
        try:
            thread.start()
            print_log(f'Thread {thread.__class__.__name__} iniciada com sucesso.')
        except Exception as e:
            print_log(f'Erro ao iniciar a thread {thread.__class__.__name__}: {e}')

    def verifica_dados_local(self):
        try:
            print_log("Pegando dados locais - MaxServices")
            for cnpj, dados_cnpj in CNPJ_CONFIG['sistema'].items():
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
                        con = FIREBIRD_CONNECTION
                        cur = con.cursor()
                        comando = 'Liberar' if ativo == "1" else 'Bloquear'
                        print_log(f"Comando para {comando} maxsuport - MaxServices")
                        cur.execute(f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}'")
                        con.commit()
                    except fdb.fbcore.DatabaseError as e:
                        print_log(f"Erro ao executar consulta: {e}")
        
        except Exception as e:
            print_log(f"Erro: {self._svc_name_} {e} - MaxServices")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxServices)
