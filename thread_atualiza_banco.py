import fdb
from funcoes import threading, os, json, datetime, marca_banco_atualizado, extrair_metadados, gerar_scripts_diferencas, executar_scripts_sql, print_log, check_banco_atualizar,carregar_configuracoes
import parametros

class threadatualizabanco(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.atualiza_banco()

    def atualiza_banco(self):
        while not self.event.wait(10):
            carregar_configuracoes()
            try:
                for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
                    ativo = dados_cnpj['sistema_ativo'] == '1'
                    sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                    caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                    porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
                    caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']

                    if ativo and sistema_em_uso == '1':
                        print_log('Vou checar se é para atualizar', 'Atualiza_Banco')
                        if check_banco_atualizar() == 1:
                            server_origem = "177.153.69.3"
                            port_origem = 3050
                            path_origem = "/home/maxsuport/base/maxsuport/dados.fdb"

                            server_destino = "127.0.0.1"
                            port_destino = porta_firebird_maxsuport
                            path_destino = caminho_base_dados_maxsuport
                            user_destino = parametros.USERFB
                            password_destino = parametros.PASSFB

                            dsn_origem = f"{server_origem}/{port_origem}:{path_origem}"
                            dsn_destino = f"{server_destino}/{port_destino}:{path_destino}"

                            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')

                            conexao_origem = fdb.connect(dsn=dsn_origem, user=parametros.USERFB, password=parametros.PASSFB)
                            conexao_destino = fdb.connect(dsn=dsn_destino, user=user_destino, password=password_destino)

                            metadados_origem = extrair_metadados(conexao_origem)
                            metadados_destino = extrair_metadados(conexao_destino)
                            
                            scripts_sql = gerar_scripts_diferencas(metadados_origem, metadados_destino)

                            erros = executar_scripts_sql(conexao_destino, scripts_sql)

                            if erros:
                                print_log("Erros encontrados durante a execução dos scripts:", "Atualiza_Banco")
                                for erro in erros:
                                    print_log(f"    Script: {erro['script']}\nErro: {erro['erro']}\n", 'Atualiza_Banco')
                            else:
                                print_log('Todos os scripts foram executados com sucesso.', 'Atualiza_Banco')

                            marca_banco_atualizado()
                            print_log('Tabela atualizada', "Atualiza_Banco")
            except Exception as e:
                print_log(f"Erro na atualização do banco: {e}", "Atualiza_Banco")

# Inicializar a thread
if __name__ == "__main__":
    thread = threadatualizabanco()
    thread.start()
