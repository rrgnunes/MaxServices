import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from utils.salva_metadados_json import salva_metadados_mysql, salva_json_metadados_local
from funcoes.funcoes import (
    print_log,
    pode_executar,
    criar_bloqueio,
    obter_dados_ini,
    remover_bloqueio,
    apagar_itens_pasta,
    inicializa_conexao_mysql,
    comparar_metadados_mysql,
    executar_scripts_meta_mysql,
)


def atualiza_banco_mysql(banco):

    metadados_origem = os.path.join(params.SCRIPT_PATH, 'data', 'metadados_local')
    metadados_destino = os.path.join(params.SCRIPT_PATH, 'data', f'metadados_mysql_{banco}')

    apagar_itens_pasta(metadados_origem)
    apagar_itens_pasta(metadados_destino)

    info = obter_dados_ini(os.path.join(params.SCRIPT_PATH.replace('SERVER', ''), 'banco.ini'))
    salva_json_metadados_local(info['caminho_banco'])
    salva_metadados_mysql(banco)


    if not os.path.exists(metadados_origem):
        raise 'Pasta de metadados de origem não existe.'
    
    if not os.path.exists(metadados_destino):
        raise 'Pasta de mestadados de destino não existe.'
    
    scripts = comparar_metadados_mysql(metadados_origem, metadados_destino)

    params.BASEMYSQL = banco
    # params.HOSTMYSQL = 'localhost'
    inicializa_conexao_mysql()

    erros = executar_scripts_meta_mysql(scripts, params.MYSQL_CONNECTION)

    if erros:
        print_log(f"Erros durante ocorridos durante atualização:", nome_script)
        for erro in erros:
            print_log(erro, nome_script)

    if params.MYSQL_CONNECTION:
        if params.MYSQL_CONNECTION.is_connected():
            params.MYSQL_CONNECTION.close()
    



if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            atualiza_banco_mysql('DADOSHM')
        except Exception as e:
            print_log(f'Não foi possível atualizar banco de dados mysql -> motivo: {e}')
        finally:
            remover_bloqueio(nome_script)