from funcoes import *
try:
    import funcao_import_lib
except Exception as a:
    print_log(a)
import win32serviceutil
import win32service
import win32event
import servicemanager
import urllib.request
import os
import sys
import subprocess
import requests
import time
import json

import psutil
import ctypes

#21:44
MAXSERVICES = 'MaxServices'
SERVICE_NAME = 'MaxUpdate'
SCRIPT_URL = 'https://maxsuport.com.br/static/update/servico.py'
SCRIPT_PATH_REMOTO = 'https://maxsuport.com.br/static/update/'
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
SERVICE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'servico.py')
SERVICE_DISPLAY_NAME = 'MaxUpdate'
PASTA_MAXSUPORT = SCRIPT_PATH.split('/')[0] + '/' + SCRIPT_PATH.split('/')[1]


class MaxUpdate(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = 'Monitora atualizações'
    _executar = True

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self._executar = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        while self._executar:
            SCRIPT_PATH_REMOTO = "https://maxsuport.com.br/static/update/"
            try:
                
                print_log('Bem... Vamos lá')

                print_log('Vou verificar se o banco.db existe, senão criarei')

                verifica_sqlite()

                print_log('Tudo ok com o banco de dados sqlite')

                versao_online = 0

                # Substitua pelo URL da página que deseja obter o conteúdo
                url = "https://maxsuport.com.br/static/update/versao.txt"

                # Faz a requisição GET para a página
                response = requests.get(url, timeout=5)

                # Verifica se a requisição foi bem-sucedida (código de status 200)
                if response.status_code == 200:
                    # Obtém o conteúdo da página como uma string
                    versao_online = int(response.text)
                    print_log('Versão online ' + str(versao_online))

                else:
                    print_log("Erro ao obter o conteúdo da página:",
                          response.status_code)
            except Exception as a:
                print_log(a)

            versao_local = 0
            try:
                with open(SCRIPT_PATH + 'versao.txt', 'r') as arquivo:
                    versao_local = int(arquivo.read())
            except:
                print_log('Arquivo da versão local não encontrado')

            print_log('Versão local ' + str(versao_local))

            if versao_online > versao_local:
                print_log('Então vamos atualizar')
                try:
                    # Desativar o serviço
                    try:
                        win32serviceutil.StopService(MAXSERVICES)
                        print_log('Serviço parado')
                    except:
                        print_log('Serviço nao encontrado')

                    try:
                        win32serviceutil.RemoveService(MAXSERVICES)
                        print_log('Serviço removido')
                    except:
                        print_log('Serviço nao removido')

                    # Baixar o novo script
                    # fonte novo
                    lista_arquivos = ['servico.py','config.json','parametros.py','funcoes.py',
                                      'thread_backup_local.py','thread_verifica_remoto.py','thread_xml_contador.py',
                                      'funcao_import_lib.py','thread_atualiza_banco.py','thread_servidor_socket.py',
                                      'funcoes_zap.py','thread_zap_automato.py']

                    for arquivo in lista_arquivos:
                        urllib.request.urlretrieve(SCRIPT_PATH_REMOTO + arquivo, SCRIPT_PATH + arquivo)
                        print_log('Download efetuado do arquivo ' + arquivo)

                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python "{SERVICE_PATH}" install', shell=True)
                        print_log('Serviço instalado')
                    except:
                        print_log('Serviço nao instalado')

                    # Iniciar o novo serviço
                    try:
                        subprocess.call(
                            f'python "{SERVICE_PATH}" start', shell=True)
                        print_log('Serviço iniciado')
                    except:
                        print_log('Serviço nao iniciado')

                    with open(SCRIPT_PATH + 'versao.txt', 'w') as arquivo:
                        arquivo.write(str(versao_online))

                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                          servicemanager.PYS_SERVICE_STARTED,
                                          (SERVICE_DISPLAY_NAME, ''))
                except Exception as e:
                    print_log(e)
                    # Lidar com erros de download, atualização ou instalação
                    servicemanager.LogErrorMsg(
                        f"Erro: {str(e)}")
            else:
                # Check if the service is running
                try:
                    service_status = win32serviceutil.QueryServiceStatus(MAXSERVICES)[
                        1]
                    if service_status == win32service.SERVICE_RUNNING:
                        print_log("Serviço está rodando")
                    else:
                        # Iniciar o novo serviço
                        try:
                            subprocess.call(
                                f'python "{SERVICE_PATH}" start', shell=True)
                            print_log('Serviço iniciado')
                        except:
                            print_log('Serviço nao iniciado')
                except:
                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python "{SERVICE_PATH}" install', shell=True)
                        print_log('Serviço instalado')
                    except:
                        print_log('Serviço nao instalado')

            #Verifico a atualização do maxservices  
            try:
                versao_online = VerificaVersaoOnline('versaosistema')
                versao_local = 0
                try:
                    with open(SCRIPT_PATH + 'versaosistema.txt', 'r') as arquivo:
                        versao_local = int(arquivo.read())
                except:
                    print_log('Arquivo da versão sistema local não encontrado')

                if versao_online > versao_local:
                    print_log('Achei versão nova do executável')
                    marca_versao_nova_exe()
                    retorno_atualizacao = atualizar_versao_nova_exe()
                    if ((retorno_atualizacao is None) or (retorno_atualizacao == 1)):
                        try:
                            # Desativar o executavel
                            try:
                                for proc in psutil.process_iter(['name', 'exe']):
                                    if 'Retaguarda' in proc.info['name']:
                                        proc.kill()
                                print_log('Executavel parado')
                            except:
                                print_log('Executavel nao encontrado')

                            # Baixar o novo executavel
                            lista_arquivos = ['Retaguarda.exe','dados.db']

                            for arquivo in lista_arquivos:
                                if arquivo == 'dados.db':
                                    if not os.path.isfile(PASTA_MAXSUPORT + 'dados/' + arquivo):
                                        urllib.request.urlretrieve(SCRIPT_PATH_REMOTO + arquivo, PASTA_MAXSUPORT + 'dados/'+ arquivo)
                                else:
                                    urllib.request.urlretrieve(SCRIPT_PATH_REMOTO + arquivo, PASTA_MAXSUPORT + arquivo)

                                print_log(f'Download do MaxServices {SCRIPT_PATH_REMOTO}{arquivo}')
                                print_log(f'Na Pasta {PASTA_MAXSUPORT}{arquivo}')
                                print_log(f'Download do MaxServices efetuado')

                            # Cria tarefas no agendador windows
                            try:
                                print_log('Versão atualizada com sucesso')

                                marca_versao_atualizada()

                            except Exception as e:
                                print_log(e)

                            with open(SCRIPT_PATH + 'versaomaxservices.txt', 'w') as arquivo:
                                arquivo.write(str(versao_online))

                            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                                servicemanager.PYS_SERVICE_STARTED,
                                                (SERVICE_DISPLAY_NAME, ''))
                        except Exception as e:
                            print_log(e)
                            # Lidar com erros de download, atualização ou instalação
                            servicemanager.LogErrorMsg(
                                f"Erro: {str(e)}")
                        
            except Exception as e:
                print_log(e)
                # Lidar com erros de download, atualização ou instalação
                servicemanager.LogErrorMsg(
                    f"Erro: {str(e)}")


            # Aguardar antes de verificar novamente por atualizações
            print_log('Agora vou dormir 10 segundos')
            time.sleep(10)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxUpdate)
    
