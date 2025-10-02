import fdb
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from utils.salva_metadados_json import salva_metadados_mysql
from funcoes.funcoes import (
    print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    extrair_metadados,
    executar_scripts_mysql,
    extrair_metadados_mysql,
    buscar_estrutura_remota,
    comparar_metadados_mysql,
    gerar_scripts_diferentes_mysql,
    inicializa_conexao_mysql_replicador
)

def atualiza_banco_mysql():
    bancos_mysql = ['DADOSHM']
    pasta_metadados_remota = os.path.join(parametros.SCRIPT_PATH, 'data','metadados_remoto')

    try:

        print_log('Verificando se precisa atualizar banco remoto', nome_script)

        # try:
        #     fdb.load_api('/home/MaxServices/libs/libfbclient.so.2.5.9')
        #     server_origem = "maxsuportsistemas.com"
        #     port_origem = 3050
        #     path_origem = "/home/base/dados.fdb"
        #     dsn_origem = f"{server_origem}/{port_origem}:{path_origem}"
        #     conexao_origem_fb = fdb.connect(dsn=dsn_origem, user='SYSDBA', password='masterkey')
        #     print_log('Conexao firebird estabelecida com sucesso', nome_script)

        # except Exception as a:
        #     print_log(f'Nao foi possivel conectar em banco origem firebird: {a}', nome_script)

        # metadados_origem = extrair_metadados(conexao_origem_fb)

        # inicializa_conexao_mysql_replicador()
        # conexao_destino_mysql = parametros.MYSQL_CONNECTION_REPLICADOR
        # metadados_destino = extrair_metadados_mysql(conexao_destino_mysql)
        # scripts = gerar_scripts_diferentes_mysql(metadados_origem, metadados_destino)
        # erros = executar_scripts_mysql(conexao_destino_mysql, scripts, nome_script)

        # for erro in erros:
        #     print_log(f"nao foi possivel executar: {erro}")
        # parametros.MYSQL_CONNECTION_REPLICADOR.close()
        
        # buscar_estrutura_remota()
        for banco in bancos_mysql:
            # salva_metadados_mysql(banco)
            pasta_metadados_mysql = os.path.join(parametros.SCRIPT_PATH, 'data',f'metadados_mysql_{banco}')

        scripts = comparar_metadados_mysql(pasta_metadados_remota, pasta_metadados_mysql)

        print('acabou')

    except Exception as e:
        print_log(f'{e}', nome_script)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)

        try:
            atualiza_banco_mysql()

        except Exception as e:
            print_log(f'Ocorreu um erro na execução - motivo: {e}')

        finally:
            remover_bloqueio(nome_script)
