from funcoes import *


# thread do alerta bloqueio
class threadalertabloqueio(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.interval):
            self.alertabloqueio()
            time.sleep(self.interval)

    def alertabloqueio(self):
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
