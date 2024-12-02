import sys
import fdb
from funcoes import os, extrair_metadados, gerar_scripts_diferencas, executar_scripts_sql, print_log, carregar_configuracoes, criar_bloqueio, remover_bloqueio, pode_executar
import parametros
import configparser
import os

def atualiza_banco():
    nome_servico = 'thread_atualiza_banco'
    carregar_configuracoes()
    try:

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
                print_log('Vou checar se é para atualizar', nome_servico)
                atualiza_banco = 0

                if 'manutencao' in config and 'atualizabanco' in config['manutencao']:
                    atualiza_banco = config['manutencao']['atualizabanco']

                if str(atualiza_banco) == '1':
                    server_origem = "maxsuportsistemas.com"
                    port_origem = 3050
                    path_origem = "/home/base/dados.fdb"

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
                        print_log("Erros encontrados durante a execução dos scripts:", nome_servico)
                        for erro in erros:
                            print_log(f"    Script: {erro['script']}\nErro: {erro['erro']}\n", nome_servico)
                    else:
                        print_log('Todos os scripts foram executados com sucesso.', nome_servico)

                    config['manutencao']['atualizabanco'] = '0'

                    # Salva as mudanças de volta no arquivo INI
                    with open(SCRIPT_PATH + '/banco.ini', 'w') as configfile:
                        config.write(configfile)

                    print_log('Tabela atualizada', nome_servico)
    except Exception as e:
        print_log(f"Erro na atualização do banco: {e}", nome_servico)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            atualiza_banco()
        except Exception as e:
            print_log(f'Ocorreu um erro na execução - motivo: {e}', nome_script)
        finally:
            remover_bloqueio(nome_script)