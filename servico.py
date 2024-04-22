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
import ctypes
from ctypes.wintypes import DWORD, LPWSTR, BOOL

try:
    from thread_verifica_remoto import *
    from thread_backup_local import *
    from thread_servidor_socket import *
    from thread_xml_contador import *
    from thread_atualiza_banco import *
    from thread_zap_automato import *
except:
    print('Erro ao carregar import')

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
# Configuração do logger
logger = logging.getLogger('my_logger')


def print_log(texto):
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')

def exibe_alerta():
    comando = f'start http://maxsuport.com.br/alerta.html'
    # Executando o comando
    subprocess.run(comando, shell=True)

class MaxServices(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaxServices"
    _svc_display_name_ = "MaxServices"
    _svc_description_ = "Monitora uso de sistema e dados"

    #21:47
    MAXUPDATE = 'MaxUpdate'
    SCRIPT_URL = 'https://maxsuport.com.br/static/update/MaxUpdate.py'
    SERVICE_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'MaxUpdate.py')

    logger.setLevel(logging.DEBUG)
    # Configuração do handler
    log_file = SCRIPT_PATH + 'maxservices.log'
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

    def __init__(self, args):
        super().__init__(args)
        try:
            self.timer_thread_remoto = threadverificaremoto()
            self.timer_thread_backup = threadbackuplocal()  
            self.timer_thread_servidor_socket = threadservidorsocket()
            self.timer_thread_xml_contador = threadxmlcontador()
            self.timer_thread_atualiza_banco = threadatualizabanco()
            self.timer_thread_zap_automato= threadzapautomato()
        except Exception as a:
            print_log('Erro no init: não carregou as threads')
        self.stop = False
    
    def SvcStop(self):
        try:
            self.timer_thread_remoto.event.set()
            self.timer_thread_backup.event.set()
            self.timer_thread_servidor_socket.event.set()
            self.timer_thread_xml_contador.event.set()
            self.timer_thread_atualiza_banco.event.set()
            self.timer_thread_zap_automato.event.set()
        except Exception as a:
            print_log('Erro no stop: Não parou as threads ')        
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop = True

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        while not self.stop:
            # Verifico se é servidor ou estação


            # Verifico se é produção ou homologação
            producao = 1

            # path_config_thread = SCRIPT_PATH + "/config.json"
            # if os.path.exists(path_config_thread):
            #     with open(path_config_thread, 'r') as config_file:
            #         config_thread = json.load(config_file)
            #         producao = config_thread['producao']
            
            SCRIPT_URL = 'https://maxsuport.com.br/static/update/MaxUpdate.py'

            try:
                print_log('Bem... Vamos lá')
                versao_online = 0

                # Substitua pelo URL da página que deseja obter o conteúdo
                url = "https://maxsuport.com.br/static/update/versaoupdate.txt"

                # Faz a requisição GET para a página
                response = requests.get(url, timeout=5)

                # Verifica se a requisição foi bem-sucedida (código de status 200)
                if response.status_code == 200:
                    # Obtém o conteúdo da página como uma string
                    versao_online = int(response.text)
                    print_log('Versão online ' + str(versao_online))
                else:
                    print_log("Erro ao obter o conteúdo da página:" + response.status_code)
                    
            except Exception as a:
                print_log(a)

            versao_local = 0
            try:
                with open(SCRIPT_PATH + 'versaoupdate.txt', 'r') as arquivo:
                    versao_local = int(arquivo.read())
            except:
                print_log('Arquivo da versão local não encontrado')

            print_log('Versão local ' + str(versao_local))

            if versao_online > versao_local:
                print_log('Então vamos atualizar')
                try:
                    # Desativar o serviço
                    try:
                        win32serviceutil.StopService(self.MAXUPDATE)
                        print_log('Serviço parado')
                    except:
                        print_log('Serviço nao encontrado')

                    try:
                        win32serviceutil.RemoveService(self.MAXUPDATE)
                        print_log('Serviço removido')
                    except:
                        print_log('Serviço nao removido')

                    # Baixar o novo script
                    # fonte novo
                    urllib.request.urlretrieve(
                        SCRIPT_URL, SCRIPT_PATH + 'MaxUpdate.py')
                    print_log('Download efetuado')

                    # Instalar o novo serviço
                    try:
                        comando = f'python "{self.SERVICE_PATH}" install'
                        print_log(f'executando comando {comando}')

                        subprocess.call(f'{comando}', shell=True)
                        print_log(f'Serviço instalado {self.SERVICE_PATH}')
                    except:
                        print_log('Serviço nao instalado')

                    # Iniciar o novo serviço
                    try:
                        comando = f'python "{self.SERVICE_PATH}" start'
                        print_log(f'executando comando {comando}')

                        subprocess.call(f'{comando}', shell=True)
                        print_log('Serviço iniciado {self.SERVICE_PATH}')
                    except:
                        print_log('Serviço nao iniciado')

                    with open(SCRIPT_PATH + 'versaoupdate.txt', 'w') as arquivo:
                        arquivo.write(str(versao_online))

                    print_log('versão update salvo')

                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                        servicemanager.PYS_SERVICE_STARTED,
                                        (self._svc_display_name_, ''))
                except Exception as e:
                    print_log(e)
                    # Lidar com erros de download, atualização ou instalação
                    servicemanager.LogErrorMsg(
                        f"Erro: {str(e)}")
            else:
                # Check if the service is running
                try:
                    service_status = win32serviceutil.QueryServiceStatus(self.MAXUPDATE)[
                        1]
                    if service_status == win32service.SERVICE_RUNNING:
                        print_log("Serviço está rodando")
                    else:
                        # Iniciar o novo serviço
                        try:
                            subprocess.call(
                                f'python "{self.SERVICE_PATH}" start', shell=True)
                            print_log(f'Serviço iniciado {self.SERVICE_PATH}')
                        except:
                            print_log('Serviço nao iniciado')
                except:
                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python "{self.SERVICE_PATH}" install', shell=True)
                        print_log(f'Serviço instalado {self.SERVICE_PATH}')
                    except:
                        print_log('Serviço nao instalado')

            print_log('Start no verifica remoto')

            try:
                self.timer_thread_remoto.start()
            except Exception as a:
                print_log(f'Erro no start do verifica remoto - {a}');            

            print_log('Start no backup')
            try:
                self.timer_thread_backup.start()
            except Exception as a:
                print_log(f'Erro no start do backup- {a}');        

            # print_log('Start no alerta de bloqueio')
            # try:
            #     self.timer_thread_alerta_bloqueio.start()
            # except Exception as a:
            #     print_log(f'Erro no start do alerta de bloqueio - {a}');        
            
            print_log('Start no xml contador')
            try:
                self.timer_thread_xml_contador.start()
            except Exception as a:
                print_log(f'Erro no start do xml contador - {a}');
            
            print_log('Start no Atualiza Banco')
            try:
                self.timer_thread_atualiza_banco.start()
            except Exception as a:
                print_log(f'Erro no start do Atualiza Banco - {a}');            
            
            print_log('Start no Servidor Socket')
            try:
                self.timer_thread_servidor_socket.start()
            except Exception as a:
                print_log(f'Erro no start do Servidor Socket - {a}');         

            print_log('Start no Zap automato')
            try:
                self.timer_thread_zap_automato.start()
            except Exception as a:
                print_log(f'Erro no start do Zap automato - {a}');                        
        
            try:
                print_log(f"pega dados local - MaxServices") 

                if os.path.exists("C:/Users/Public/config.json"):
                    with open('C:/Users/Public/config.json', 'r') as config_file:
                        config = json.load(config_file)
                    # Ler arquivo INI
                    # Acessar valor
                        
                    for cnpj in config['sistema']:
                        parametros = config['sistema'][cnpj]
                        ativo = parametros['sistema_ativo']
                        sistema_em_uso = parametros['sistema_em_uso_id']
                        caminho_base_dados_gfil = parametros['caminho_base_dados_gfil'].replace(
                            '\\', '/')
                        caminho_base_dados_gfil = caminho_base_dados_gfil.split(
                            '/')[0] + '/' + caminho_base_dados_gfil.split('/')[1]
                        caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                        caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                        porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                        ip = parametros['ip']
 
                        BANCO_SQLITE = os.path.dirname(caminho_base_dados_maxsuport)

                        print_log(
                            f"local valor {ativo} do cnpj {cnpj} - MaxServices")

                        if ativo == "0" and sistema_em_uso == "2":
                            print_log(
                                f"Encerra Processo do GFIL - MaxServices")
                            for proc in psutil.process_iter(['name', 'exe']):
                                if 'FIL' in proc.info['name']:
                                    if caminho_base_dados_gfil in proc.info['exe'].replace('\\', '/'):
                                        print_log(
                                            f"Encerra Processo do GFIL na proc {caminho_base_dados_gfil}, no caminho {proc.info['exe']}- MaxServices")
                                        proc.kill()
                                        print_log(
                                            f"Iniciar conexão com alerta - MaxServices")
                                        exibe_alerta()

                        if sistema_em_uso == "1":
                            data_cripto = '80E854C4A6929988F97AE2'
                            if ativo == "1":
                                data_cripto = '80E854C4A6929988F879E1'
                            try:
                                path_dll = f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll'
                                fdb.load_api(path_dll)
                                print_log(f'Carregando dll: {path_dll}')
                                con = fdb.connect(
                                    host='localhost',
                                    database=caminho_base_dados_maxsuport,
                                    user='maxsuport',
                                    password='oC8qUsDp',
                                    port=int(porta_firebird_maxsuport)
                                )
                                comando = 'Liberar'
                                if ativo == "0":
                                    comando = 'Bloquear'
                                print_log(
                                    f"Comando para {comando} maxsuport- MaxServices")

                                cur = con.cursor()
                                cur.execute(
                                    f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}' ")
                                con.commit()
                                con.close()
                                # if ativo == "0":
                                #    exibe_alerta(
                                #        "1Sistema bloqueado por inadimplência de mensalidades.\nEntre em contato com o suporte!\n(66) 99926-4708\n(66) 99635-3159\n(66) 99935-3355\n-------------------------------\nAtenciosamente\nMax Suport Sistemas;")

                            except fdb.fbcore.DatabaseError as e:
                                # Lidar com a exceção
                                print_log("Erro ao executar consulta:" + e)
            
            except Exception as a:
                print_log(f"Erro: {self._svc_name_} {a} - MaxServices")


                        # Aguardar antes de verificar novamente por atualizações
            print_log('Agora vou dormir 10 segundos')
            time.sleep(10)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxServices)
