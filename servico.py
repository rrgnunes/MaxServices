import win32serviceutil
import win32service
import servicemanager
from thread_verifica_remoto import *
from thread_backup_local import *
from thread_alerta_bloqueio import *
from thread_xml_contador import *
import requests
from funcoes import print_log
import urllib.request
import win32event


MAXSERVICES = 'MaxUpdate'
SCRIPT_URL = 'http://maxsuport.com.br:81/static/update/MaxUpdate.py'
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
SERVICE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'MaxUpdate.py')

class MaxServices(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaxServices"
    _svc_display_name_ = "MaxServices"
    _svc_description_ = "Monitora uso de sistema e dados"

    def __init__(self, args):
        super().__init__(args)
        self.timer_thread_remoto = threadverificaremoto()
        self.timer_thread_backup = threadbackuplocal()  
        self.timer_thread_alerta_bloqueio = threadalertabloqueio()
        self.timer_thread_xml_contador = threadxmlcontador()
        self.stop = False
    

    def SvcStop(self):
        self.timer_thread_remoto.event.set()
        self.timer_thread_backup.event.set()
        self.timer_thread_alerta_bloqueio.event.set()
        self.timer_thread_xml_contador.event.set()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop = True

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        # Verifico se é produção ou homologação
        producao = -1
        while producao == -1:
            path_config_thread = SCRIPT_PATH + "/config.json"
            if os.path.exists(path_config_thread):
                with open(path_config_thread, 'r') as config_file:
                    config_thread = json.load(config_file)
            producao = config_thread['producao']
        if producao == 0:
            SCRIPT_URL = 'http://maxsuport.com.br:81/static/hom_update/MaxUpdate.py'

        print_log('Start no verifica remoto')
        try:
            self.timer_thread_remoto.start()
        except Exception as a:
            print_log('Erro no start do verifica remoto - ' + a);            

        print_log('Start no backup')
        try:
            self.timer_thread_backup.start()
        except Exception as a:
            print_log('Erro no start do backup- ' + a);        

        print_log('Start no alerta de bloqueio')
        try:
            self.timer_thread_alerta_bloqueio.start()
        except Exception as a:
            print_log('Erro no start do alerta de bloqueio - ' + a);        
        
        print_log('Start no xml contador')
        try:
            self.timer_thread_xml_contador.start()
        except Exception as a:
            print_log('Erro no start do xml contador - ' + a);

        while not self.stop:
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
                                        exibe_alerta(
                                            "1Sistema bloqueado por inadimplência de mensalidades.\nEntre em contato com o suporte!\n(66) 99926-4708\n(66) 99635-3159\n(66) 99935-3355\n-------------------------------\nAtenciosamente\nMax Suport Sistemas;")

                        if sistema_em_uso == "1":
                            data_cripto = '80E854C4A6929988F97AE2'
                            if ativo == "1":
                                data_cripto = '80E854C4A6929988F879E1'
                            try:
                                con = fdb.connect(
                                    host='localhost',
                                    database=caminho_base_dados_maxsuport,
                                    user='sysdba',
                                    password='masterkey',
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
                                print_log("Erro ao executar consulta:", e)
            
            except Exception as a:
                print_log(f"local valor {self._svc_name_} {a} - MaxServices")


            try:
                print_log('Bem... Vamos lá')
                versao_online = 0

                # Substitua pelo URL da página que deseja obter o conteúdo
                url = "http://maxsuport.com.br:81/static/update/versaoupdate.txt"
                if producao == 0:
                    url = "http://maxsuport.com.br:81/static/hom_update/versaoupdate.txt"

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
                    urllib.request.urlretrieve(
                        SCRIPT_URL, SCRIPT_PATH + 'MaxUpdate.py')
                    print_log('Download efetuado')

                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} install', shell=True)
                        print_log('Serviço instalado')
                    except:
                        print_log('Serviço nao instalado')

                    # Iniciar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} start', shell=True)
                        print_log('Serviço iniciado')
                    except:
                        print_log('Serviço nao iniciado')

                    with open(SCRIPT_PATH + 'versao.txt', 'w') as arquivo:
                        arquivo.write(str(versao_online))

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
                    service_status = win32serviceutil.QueryServiceStatus(MAXSERVICES)[
                        1]
                    if service_status == win32service.SERVICE_RUNNING:
                        print_log("Serviço está rodando")
                    else:
                        # Iniciar o novo serviço
                        try:
                            subprocess.call(
                                f'python {SERVICE_PATH} start', shell=True)
                            print_log('Serviço iniciado')
                        except:
                            print_log('Serviço nao iniciado')
                except:
                    # Instalar o novo serviço
                    try:
                        subprocess.call(
                            f'python {SERVICE_PATH} install', shell=True)
                        print_log('Serviço instalado')
                    except:
                        print_log('Serviço nao instalado')
            # Aguardar antes de verificar novamente por atualizações
            print_log('Agora vou dormir 10 segundos')
            win32event.WaitForSingleObject(
                self.hWaitStop, 10000)  # Aguarda 1 minuto

            time.sleep(7)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxServices)
