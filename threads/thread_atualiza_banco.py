import os
import sys
import fdb
import configparser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from utils.salva_metadados_json import salva_json_metadados_local
from funcoes.funcoes import os, print_log, criar_bloqueio, remover_bloqueio, pode_executar, carrega_arquivo_config, buscar_estrutura_remota, comparar_metadados, executar_scripts_meta, inicializa_conexao_firebird, verifica_dll_firebird


def atualiza_banco():
    nome_servico = 'thread_atualiza_banco'
    pasta_metadados_local = os.path.join(parametros.SCRIPT_PATH, 'data', 'metadados_local')
    pasta_metadados_remoto = os.path.join(parametros.SCRIPT_PATH, 'data','metadados_remoto')
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
            
            # Pula para a proxima configuracao caso o banco de dados não exista
            if not os.path.exists(caminho_base_dados_maxsuport):
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
                        print_log('Iniciando comparação de estrutura...', nome_servico)
                        script = comparar_metadados(pasta_metadados_remoto, pasta_metadados_local)
                        try:
                            parametros.DATABASEFB = caminho_base_dados_maxsuport
                            parametros.FIREBIRD_CONNECTION = None
                            parametros.USERFB = 'MAXSUPORT'
                            inicializa_conexao_firebird()

                            erros = executar_scripts_meta(script, parametros.FIREBIRD_CONNECTION)
                            
                            permissoes_maxservices()
                            if erros:
                                print_log('Erros ao executar o script:', nome_servico)
                                for erro in erros:
                                    print_log(erro, nome_servico)

                            config['manutencao']['atualizabanco'] = '0'
                            with open(caminho_ini, 'w') as configfile:
                                config.write(configfile)
                            config.clear                            

                            procedures = ['CREATE_TRIGGERS_GENERATOR', 'CREATE_TRIGGERS_INSERT', 'CREATE_TRIGGERS_REPLICADOR', 'CREATE_TRIGGER_BLOCK'] 
                            try:
                                cursor: fdb.Cursor = parametros.FIREBIRD_CONNECTION.cursor()
                                for procedure in procedures:
                                    try:
                                        cursor.execute(f'EXECUTE PROCEDURE {procedure}')
                                        parametros.FIREBIRD_CONNECTION.commit()
                                    except Exception as e:
                                        print_log(f'Não foi possível executar procedure "{procedure}", motivo: {e}')
                                        continue
                            except Exception as e:
                                print_log(f'Não foi possivel executar procedures -> motivo: {e}')

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

def permissoes_maxservices():
    try:
        print_log('Iniciando permissões para MaxServices...', nome_script)
        select_sql = """select trim(rr.rdb$relation_name) as tabela from rdb$relations rr
                        where rr.rdb$system_flag = 0 and rr.rdb$relation_name <> 'IBE$REPORTS'
                        order by rr.rdb$relation_name"""
        cur:fdb.Cursor = parametros.FIREBIRD_CONNECTION.cursor()
        cur.execute(select_sql)
        tabelas = cur.fetchall()
        print_log('Executando permissções...', nome_script)
        for tabela in tabelas:
            try:
                sql = f"GRANT ALL ON {tabela[0]} TO MAXSERVICES WITH GRANT OPTION;"
                print_log(sql, nome_script)
                cur.execute(sql)
                parametros.FIREBIRD_CONNECTION.commit()
            except Exception as e:
                print(f"Erro ao dar permissão na tabela {tabela[0]}, motivo: {e}")
                parametros.FIREBIRD_CONNECTION.rollback()

    except Exception as e:
        print_log(f'Erro ao realizar permissões do usuario -> motivo: {e}')

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