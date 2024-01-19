from funcoes import *

# thread do alerta bloqueio
class threadalertabloqueio(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.alertabloqueio()
            

    def alertabloqueio(self):
        print_log(f"Carrega configurações da thread - AlertaBloqueio")
        intervalo = -1
        while intervalo == -1:
            path_config_thread = SCRIPT_PATH + "/config.json"
            if os.path.exists(path_config_thread):
                with open(path_config_thread, 'r') as config_file:
                    config_thread = json.load(config_file)
            intervalo = config_thread['time_thread_alertabloqueio']
        while not self.event.wait(intervalo):
            # Conexão com o banco de dados
            try:
                print_log(f"pega dados local - alertabloqueio")
                if os.path.exists("C:/Users/Public/config.json"):
                    with open('C:/Users/Public/config.json', 'r') as config_file:
                        config = json.load(config_file)
                    for cnpj in config['sistema']:
                        parametros = config['sistema'][cnpj]
                        alerta_bloqueio = parametros['alerta_bloqueio'] == '1'

                        if alerta_bloqueio:
                            exibe_alerta(
                                "2Seu sistema poderá ser bloqueado em breve por inadimplência de mensalidades.\nContatos:\n(66) 99926-4708 / 99635-3159 / 99935-3355;")

            except Exception as a:
                # self.logger.error(f"{self._svc_name_} {a}.")
                print_log(a)
        time.sleep(intervalo)
