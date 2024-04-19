import fdb
from funcoes import threading,os,json,datetime, marca_banco_atualizado,extrair_metadados,gerar_scripts_diferencas,executar_scripts_sql,print_log,check_banco_atualizar



# thread do backup
class threadatualizabanco(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.atualizabanco()
        
    def atualizabanco(self):
        while not self.event.wait(10):
            #carrega config
            if os.path.exists("C:/Users/Public/config.json"):
                with open('C:/Users/Public/config.json', 'r') as config_file:
                    config = json.load(config_file)
                    
                for cnpj in config['sistema']:
                    parametros = config['sistema'][cnpj]
                    ativo = parametros['sistema_ativo'] == '1'
                    sistema_em_uso = parametros['sistema_em_uso_id']
                    caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                    porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                    caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                    data_hora = datetime.datetime.now()
                    data_hora_formatada = data_hora.strftime(
                        '%Y_%m_%d_%H_%M_%S')
                    print_log('Vou validar para atualizar','Atualiza_Banco')
                    if ativo == 1 and sistema_em_uso == '1':
                        banco_sqlite = os.path.dirname(caminho_base_dados_maxsuport) + '\\dados.db'
                        print_log('Vou checar se é para atualizar','Atualiza_Banco')
                        if check_banco_atualizar() == 1:
                        #if 1 == 1:
                            # Parâmetros da conexão, incluindo a porta
                            server_origem = "177.153.69.3"
                            port_origem = 3050  # Substitua pelo número da porta real, se diferente
                            path_origem = "/home/maxsuport/base/maxsuport/dados.fdb"
                            user_origem = "sysdba"
                            password_origem = "masterkey"

                            server_destino = "127.0.0.1"
                            port_destino = porta_firebird_maxsuport  # Substitua pelo número da porta real, se diferente
                            path_destino = caminho_base_dados_maxsuport
                            user_destino = "maxsuport"
                            password_destino = "oC8qUsDp"

                            # Criando as strings de conexão com a porta
                            dsn_origem = f"{server_origem}/{port_origem}:{path_origem}"
                            dsn_destino = f"{server_destino}/{port_destino}:{path_destino}"

                            #fdb.fb_library_name = 'C:/Users/rrgnu/OneDrive/Documentos/MSAtualizaBanco/fbclient.dll'

                            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')

                            # Conexões
                            conexao_origem = fdb.connect(dsn=dsn_origem, user=user_origem, password=password_origem)
                            conexao_destino = fdb.connect(dsn=dsn_destino, user=user_destino, password=password_destino)

                            metadados_origem = extrair_metadados(conexao_origem)
                            metadados_destino = extrair_metadados(conexao_destino)
                            
                            scripts_sql = gerar_scripts_diferencas(metadados_origem, metadados_destino)

                            erros = executar_scripts_sql(conexao_destino, scripts_sql)

                            if erros:
                                print_log("Erros encontrados durante a execução dos scripts:","Atualiza_Banco")
                                for erro in erros:
                                    print_log(f"    Script: {erro['script']}\nErro: {erro['erro']}\n",'Atualiza_Banco')
                            else:
                                print_log('Todos os scripts foram executados com sucesso.','Atualiza_Banco')

                            marca_banco_atualizado()
                            print_log('Tabela atualizada',"Atualiza_Banco")
                            
