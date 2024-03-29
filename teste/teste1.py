import win32serviceutil
import win32service
import win32event
import servicemanager
import urllib.request
import os
import sys
import subprocess
import requests

MAXSERVICES = 'MaxServices'
SERVICE_NAME = 'MaxUpdate'
SCRIPT_URL = 'http://maxsuport.com.br:81/static/update/servico.py'
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
SERVICE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'servico.py')
SERVICE_DISPLAY_NAME = 'MaxUpdate'
print(SERVICE_PATH)


try:
    print('Bem... Vamos lá')

    # Substitua pelo URL da página que deseja obter o conteúdo
    url = "http://maxsuport.com.br:81/static/update/versao.txt"

    # Faz a requisição GET para a página
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Obtém o conteúdo da página como uma string
        versao_online = int(response.text)
        print('Versão online ' + str(versao_online))

    else:
        print("Erro ao obter o conteúdo da página:",
                response.status_code)

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
            urllib.request.urlretrieve(
                SCRIPT_URL, SCRIPT_PATH + 'servico.py')
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

except Exception as a:
    print(a)