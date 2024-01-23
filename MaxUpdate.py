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

#21:44
MAXSERVICES = 'MaxServices'
SERVICE_NAME = 'MaxUpdate'
SCRIPT_URL = 'http://maxsuport.com.br:81/static/update/servico.py'
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
SERVICE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'servico.py')
SERVICE_DISPLAY_NAME = 'MaxUpdate'
print(SERVICE_PATH)


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
            try:
                print('Bem... Vamos lá')

                producao = 0
            
                path_config_thread = SCRIPT_PATH + "/config.json"
                if os.path.exists(path_config_thread):
                    with open(path_config_thread, 'r') as config_file:
                        config_thread = json.load(config_file)
                producao = config_thread['producao']
                
                if producao == 0:
                    SCRIPT_URL = 'http://maxsuport.com.br:81/static/hom_update/MaxUpdate.py'

                versao_online = 0

                # Substitua pelo URL da página que deseja obter o conteúdo
                url = "http://maxsuport.com.br:81/static/update/versao.txt"
                if producao == 0:
                    url = "http://maxsuport.com.br:81/static/hom_update/versao.txt"

                # Faz a requisição GET para a página
                response = requests.get(url, timeout=5)

                # Verifica se a requisição foi bem-sucedida (código de status 200)
                if response.status_code == 200:
                    # Obtém o conteúdo da página como uma string
                    versao_online = int(response.text)
                    print('Versão online ' + str(versao_online))

                else:
                    print("Erro ao obter o conteúdo da página:",
                          response.status_code)
            except Exception as a:
                print(a)

            versao_local = 0
            try:
                with open(SCRIPT_PATH + 'versao.txt', 'r') as arquivo:
                    versao_local = int(arquivo.read())
            except:
                print('Arquivo da versão local não encontrado')

            print('Versão local ' + str(versao_local))

            if versao_online > versao_local:
                print('Então vamos atualizar')
                try:
                    # Desativar o serviço
                    try:
                        win32serviceutil.StopService(MAXSERVICES)
                        print('Serviço parado')
                    except:
                        print('Serviço nao encontrado')

                    try:
                        win32serviceutil.RemoveService(MAXSERVICES)
                        print('Serviço removido')
                    except:
                        print('Serviço nao removido')

                    # Baixar o novo script
                    # fonte novo
                    lista_arquivos = ['servico.py','config.json','parametros.py','funcoes.py','thread_alerta_bloqueio.py',
                                      'thread_backup_local.py','thread_verifica_remoto.py','thread_xml_contador.py']

                    for arquivo in lista_arquivos:
                        urllib.request.urlretrieve(SCRIPT_URL, SCRIPT_PATH + arquivo)
                    print('Download efetuado')

                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} install', shell=True)
                        print('Serviço instalado')
                    except:
                        print('Serviço nao instalado')

                    # Iniciar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} start', shell=True)
                        print('Serviço iniciado')
                    except:
                        print('Serviço nao iniciado')

                    with open(SCRIPT_PATH + 'versao.txt', 'w') as arquivo:
                        arquivo.write(str(versao_online))

                    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                          servicemanager.PYS_SERVICE_STARTED,
                                          (SERVICE_DISPLAY_NAME, ''))
                except Exception as e:
                    print(e)
                    # Lidar com erros de download, atualização ou instalação
                    servicemanager.LogErrorMsg(
                        f"Erro: {str(e)}")
            else:
                # Check if the service is running
                try:
                    service_status = win32serviceutil.QueryServiceStatus(MAXSERVICES)[
                        1]
                    if service_status == win32service.SERVICE_RUNNING:
                        print("Serviço está rodando")
                    else:
                        # Iniciar o novo serviço
                        try:
                            subprocess.call(
                                f'python {SERVICE_PATH} start', shell=True)
                            print('Serviço iniciado')
                        except:
                            print('Serviço nao iniciado')
                except:
                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} install', shell=True)
                        print('Serviço instalado')
                    except:
                        print('Serviço nao instalado')
            # Aguardar antes de verificar novamente por atualizações
            print('Agora vou dormir 10 segundos')
            time.sleep(10)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxUpdate)
