import sys
import parametros
import configparser
import os
from salva_metadados_json import salva_json_metadados_local
from funcoes import os, extrair_metadados, gerar_scripts_diferencas, executar_scripts_sql, print_log, criar_bloqueio, remover_bloqueio, pode_executar, carrega_arquivo_config, buscar_estrutura_remota, comparar_metadados, executar_scripts_meta, inicializa_conexao_firebird


def atualiza_banco():
    nome_servico = 'thread_atualiza_banco'
    pasta_metadados_local = os.path.join(parametros.SCRIPT_PATH, 'metadados_local')
    pasta_metadados_remoto = os.path.join(parametros.SCRIPT_PATH, 'metadados_remoto')
    buscar_estrutura_remota()
    carrega_arquivo_config()
    try:
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']

            # Pula para a proxima configuracao caso nao tenha o caminho do banco de dados
            if caminho_base_dados_maxsuport.lower() == 'none':
                continue

            caminho_sistema = caminho_base_dados_maxsuport.lower().replace('\\dados\\dados.fdb', '')
            caminho_ini = os.path.join(caminho_sistema, 'banco.ini')
        

            config = configparser.ConfigParser()
            config.read(caminho_ini)

            if ativo and sistema_em_uso == '1':
                print_log(f'Verificando se pode ser atualizado -> {caminho_base_dados_maxsuport} CNPJ:{cnpj}', nome_servico)
                atualiza_banco = 0

                if ('manutencao' in config) and ('atualizabanco' in config['manutencao']):
                    atualiza_banco = config['manutencao']['atualizabanco']

                if str(atualiza_banco) == '1':

                    print_log('Salvando estrutura do banco de dados local...', nome_servico)
                    salva_json_metadados_local(caminho_base_dados_maxsuport)

                    if (os.path.exists(pasta_metadados_local)) and (os.path.exists(pasta_metadados_remoto)):
                        script = comparar_metadados(pasta_metadados_remoto, pasta_metadados_local)
                        try:
                            parametros.DATABASEFB = caminho_base_dados_maxsuport
                            parametros.FIREBIRD_CONNECTION = None
                            parametros.USERFB = 'MAXSUPORT'
                            inicializa_conexao_firebird()

                            erros = executar_scripts_meta(script, parametros.FIREBIRD_CONNECTION)
                            
                            if erros:
                                print_log('Erros ao executar o script:', nome_servico)
                                for erro in erros:
                                    print_log(erro, nome_servico)

                            config['manutencao']['atualizabanco'] = '0'
                            with open(caminho_ini, 'w') as configfile:
                                config.write(configfile)

                            config.clear

                        except Exception as e:
                            print_log(f'Erro em conexão a banco de dados -> motivo: {e}')                    
                        finally:
                            if not parametros.FIREBIRD_CONNECTION.closed:
                                parametros.FIREBIRD_CONNECTION.close()
                                parametros.FIREBIRD_CONNECTION = None
                    else:                        
                        print_log('Pasta metadados nao existe!', nome_servico)



    except Exception as e:
        print_log(f'Nao foi possivel atualizar banco de dados -> motivo: {e}', nome_servico)

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