import fdb
from funcoes import os, extrair_metadados, gerar_scripts_diferencas, executar_scripts_sql, print_log, carregar_configuracoes
import parametros
import configparser
import os
import pathlib

def atualiza_banco():
    carregar_configuracoes()
    try:
        lock_atualiza_banco = os.path.join(pathlib.Path(__file__).parent, 'lock_atualiza_banco.txt')
        if os.path.exists(lock_atualiza_banco):
            print_log('Em execucao', 'Atualiza_Banco')
            return
        else:
            with open(lock_atualiza_banco, 'w') as arq:
                arq.write('em execucao')
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
            porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
            caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']

            SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
            SCRIPT_PATH = SCRIPT_PATH.lower().replace('server','')
            # Inicializa o parser
            config = configparser.ConfigParser()

            # Carrega o arquivo INI
            config.read(SCRIPT_PATH + '/banco.ini')

            if ativo and sistema_em_uso == '1':
                print_log('Vou checar se é para atualizar', 'Atualiza_Banco')
                atualiza_banco = 0

                if 'manutencao' in config and 'atualizabanco' in config['manutencao']:
                    atualiza_banco = config['manutencao']['atualizabanco']

                if str(atualiza_banco) == '1':
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

                    conexao_origem = fdb.connect(dsn=dsn_origem, user='sysdba', password='masterkey')
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

                    config['manutencao']['atualizabanco'] = '0'

                    # Salva as mudanças de volta no arquivo INI
                    with open(SCRIPT_PATH + '/banco.ini', 'w') as configfile:
                        config.write(configfile)

                    print_log('Tabela atualizada', "Atualiza_Banco")
        os.remove(lock_atualiza_banco)
    except Exception as e:
        print_log(f"Erro na atualização do banco: {e}", "Atualiza_Banco")
        os.remove(lock_atualiza_banco)


atualiza_banco()