import win32serviceutil
import win32service
import servicemanager
from thread_verifica_remoto import *
from thread_backup_local import *
from thread_alerta_bloqueio import *
from thread_xml_contador import *

from funcoes import print_log

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
                                print("Erro ao executar consulta:", e)
            except Exception as a:
                print_log(f"local valor {self._svc_name_} {a} - MaxServices")
            time.sleep(7)






if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxServices)
