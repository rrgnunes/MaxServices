import fdb
from funcoes import threading,os,json,datetime, envia_mensagem, atualiza_ano_cliente, print_log, config_zap, retorna_pessoas, insere_mensagem_zap

# thread do backup
class threadzapautomato(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.zapautomato()

    def zapautomato(self):
        nome_servico = 'zap automato'
        while not self.event.wait(10):
            #carrega config
            print_log(f'Iniciando',nome_servico)
            if os.path.exists("C:/Users/Public/config.json"):
                with open('C:/Users/Public/config.json', 'r') as config_file:
                    config = json.load(config_file)
                for cnpj in config['sistema']:
                    try:
                        parametros = config['sistema'][cnpj]
                        ativo = parametros['sistema_ativo'] == '1'
                        sistema_em_uso = parametros['sistema_em_uso_id']
                        caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                        porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                        caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                        data_hora = datetime.datetime.now()
                        data_hora_formatada = data_hora.strftime(
                            '%Y_%m_%d_%H_%M_%S')
                        print_log(f'Vou validar para enviar mensagem',nome_servico)

                        if ativo == 1 and sistema_em_uso == '1':
                            server = "localhost"
                            port = porta_firebird_maxsuport  # Substitua pelo número da porta real, se diferente
                            path = caminho_base_dados_maxsuport
                            user = "SYSDBA"
                            password = "masterkey"
                            dsn = f"{server}/{port}:{path}"
                            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')
                            conexao = fdb.connect(dsn=dsn, user=user, password=password)
                            cfg_zap = config_zap(conexao)

                            print_log(f'Dados da configuração recebidos',nome_servico)

                            ENVIAR_MENSAGEM_ANIVERSARIO = cfg_zap['ENVIAR_MENSAGEM_ANIVERSARIO'] = 1
                            ENVIAR_MENSAGEM_PROMOCAO    = cfg_zap['ENVIAR_MENSAGEM_PROMOCAO'] = 1
                            ENVIAR_MENSAGEM_DIARIO      = cfg_zap['ENVIAR_MENSAGEM_DIARIO'] = 1
                            MENSAGEM_ANIVERSARIO        = cfg_zap['MENSAGEM_ANIVERSARIO']
                            MENSAGEM_PROMOCAO           = cfg_zap['MENSAGEM_PROMOCAO']
                            MENSAGEM_DIARIO             = cfg_zap['MENSAGEM_DIARIO']
                            DIA_MENSAGEM_DIARIA         = cfg_zap['DIA_MENSAGEM_DIARIA']
                            TIME_MENSAGEM_DIARIA        = cfg_zap['TIME_MENSAGEM_DIARIA']
                            ULTIMO_ENVIO_ANIVERSARIO    = cfg_zap['ULTIMO_ENVIO_ANIVERSARIO']
                            ULTIMO_ENVIO_DIARIO         = cfg_zap['ULTIMO_ENVIO_DIARIO']
                            ULTIMO_ENVIO_PROMOCAO       = cfg_zap['ULTIMO_ENVIO_PROMOCAO']                         

                            print_log(f'Dados da configuração recebidos',nome_servico)

                            pessoas = retorna_pessoas(conexao)

                            for pessoa in pessoas:
                                ano_atual = datetime.datetime.now().year
                                if pessoa['ANO_ENVIO_MENSAGEM_ANIVERSARIO'] != ano_atual:
                                    MENSAGEM_ANIVERSARIO = str(MENSAGEM_ANIVERSARIO).replace('@cliente',pessoa['FANTASIA'])
                                    insere_mensagem_zap(conexao, MENSAGEM_ANIVERSARIO, pessoa['CELULAR1'])
                                    atualiza_ano_cliente(conexao,pessoa['CODIGO'],ano_atual)
                                    print_log(f'Registro de aniversário criado para {pessoa["FANTASIA"]}',nome_servico)

                            envia_mensagem(conexao,cnpj)
                    except Exception as a:
                        print_log(f'{a}',nome_servico)
