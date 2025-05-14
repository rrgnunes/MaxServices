import json
import parametros
from funcoes import *

def salvar_json_metadados_master():
    pasta_metadados = os.path.join('/home', 'banco_json')
    if not os.path.exists(pasta_metadados):
        os.makedirs(pasta_metadados)
        
    try:
        print_log('Iniciando extracao de metadados.', 'salva_metadados_json')

        parametros.HOSTFB = 'maxsuportsistemas.com'
        parametros.DATABASEFB = '/home/base/dados.fdb'
        parametros.USERFB = 'SYSDBA'
        parametros.PASSFB = 'masterkey'
        parametros.PATHDLL = '/home/MaxServices/libfbclient.so.2.5.9'
        inicializa_conexao_firebird()

        with parametros.FIREBIRD_CONNECTION as con:

            # salva estrutura das tabelas
            metadados_tabelas = extrair_metadados_tabelas_firebird(con)
            if metadados_tabelas:
                with open(os.path.join(pasta_metadados,"banco.json"), 'w') as j:
                    json.dump(metadados_tabelas, j, indent=4)
                print_log('Arquivo de estrutura do banco salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar estrutura de banco', 'salva_metadados_json')

            # salva as chaves primarias das tabelas
            metadados_chaves = extrair_metadados_chaves_primarias_firebird(con)
            if metadados_chaves:
                with open(os.path.join(pasta_metadados,"chaves_primarias.json"), 'w') as j:
                    json.dump(metadados_chaves, j, indent=2)
                print_log('Arquivo de chaves primarias salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar as chaves primarias.', 'salva_metadados_json')

            # salva as chaves estrangeiras das tabelas
            metadados_chaves_estrangeiras = extrair_metadados_chaves_estrangeiras(con)
            if metadados_chaves_estrangeiras:
                with open(os.path.join(pasta_metadados,"chaves_estrangeiras.json"), 'w') as j:
                    json.dump(metadados_chaves_estrangeiras, j, indent=2)
                print_log('Arquivo de chaves estrangeiras salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar as chaves estrangeiras.', 'salva_metadados_json')

            # salva o sql das procedures
            metadados_procedures = extrair_metadados_procedures(con)
            if metadados_procedures:
                with open(os.path.join(pasta_metadados,"procedures.json"), 'w') as j:
                    json.dump(metadados_procedures, j, indent=2)
                print_log('Arquivo de procedures salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar sql das procedures.', 'salva_metadados_json')
            
            # salva o sql das triggers
            metadados_triggers = extrair_metadados_triggers(con)
            if metadados_triggers:
                with open(os.path.join(pasta_metadados,'triggers.json'), 'w') as j:
                    json.dump(metadados_triggers, j, indent=2)
                print_log('Arquivo de tiggers salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar sql das triggers.', 'salva_metadados_json')

    except Exception as e:
        print_log(f'Erro ao salvar JSONs -> motivo: {e.__class__.__name__}-{e}')

def salva_json_metadados_local(caminho_base_dados:str):
    try:
        carrega_arquivo_config()

        parametros.DATABASEFB = caminho_base_dados
        client_dll = verifica_dll_firebird()

        inicializa_conexao_firebird(client_dll)
    except Exception as e:
        print_log(f'Nao foi possivel conectar ao banco de dados -> motivo: {e}', 'salva_metadados_json')

    try:
        pasta_metadados = os.path.join(parametros.SCRIPT_PATH, 'metadados_local')
        if not os.path.exists(pasta_metadados):
            os.makedirs(pasta_metadados)

        with parametros.FIREBIRD_CONNECTION as con:

            metadados_tabelas = extrair_metadados_tabelas_firebird(con)
            if metadados_tabelas:
                with open(os.path.join(pasta_metadados,"estrutura_banco.json"), 'w') as j:
                    json.dump(metadados_tabelas, j, indent=4)
                print_log('Arquivo de estrutura do banco salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar estrutura de banco', 'salva_metadados_json')

            # salva as chaves primarias das tabelas
            metadados_chaves = extrair_metadados_chaves_primarias_firebird(con)
            if metadados_chaves:
                with open(os.path.join(pasta_metadados,"chaves_primarias.json"), 'w') as j:
                    json.dump(metadados_chaves, j, indent=2)
                print_log('Arquivo de chaves primarias salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar as chaves primarias.', 'salva_metadados_json')

            # salva as chaves estrangeiras das tabelas
            metadados_chaves_estrangeiras = extrair_metadados_chaves_estrangeiras(con)
            if metadados_chaves_estrangeiras:
                with open(os.path.join(pasta_metadados,"chaves_estrangeiras.json"), 'w') as j:
                    json.dump(metadados_chaves_estrangeiras, j, indent=2)
                print_log('Arquivo de chaves estrangeiras salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar as chaves estrangeiras.', 'salva_metadados_json')

            # salva o sql das procedures
            metadados_procedures = extrair_metadados_procedures(con)
            if metadados_procedures:
                with open(os.path.join(pasta_metadados,"procedures.json"), 'w') as j:
                    json.dump(metadados_procedures, j, indent=2)
                print_log('Arquivo de procedures salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar sql das procedures.', 'salva_metadados_json')
            
            # salva o sql das triggers
            metadados_triggers = extrair_metadados_triggers(con)
            if metadados_triggers:
                with open(os.path.join(pasta_metadados,'triggers.json'), 'w') as j:
                    json.dump(metadados_triggers, j, indent=2)
                print_log('Arquivo de tiggers salvo com sucesso', 'salva_metadados_json')
            else:
                print_log('Falha ao salvar sql das triggers.', 'salva_metadados_json')
    except Exception as e:
        print_log(f'Erro ao salvar arquivo JSON da estrutura banco local -> motivo: {e}')

if __name__ == '__main__':

    salvar_json_metadados_master()