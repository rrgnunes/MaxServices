import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from utils.salva_metadados_json import salva_json_metadados_local
from funcoes.funcoes import (
    print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    comparar_metadados,
    apagar_itens_pasta,
    executar_scripts_meta,
    verifica_dll_firebird,
    buscar_estrutura_remota,
    inicializa_conexao_firebird
)

def atualiza_banco():
    pasta_metadados_origem = os.path.join(params.SCRIPT_PATH, 'data', 'metadados_local')
    pasta_metadados_destino = os.path.join(params.SCRIPT_PATH, 'data', 'metadados_remoto')

    apagar_itens_pasta(pasta_metadados_origem)
    apagar_itens_pasta(pasta_metadados_destino)

    caminho_base_dados = "C:\\MaxSuport\\Dados\\Dados.fdb"

    buscar_estrutura_remota()
    salva_json_metadados_local(caminho_base_dados, pasta_metadados_origem)

    scripts = comparar_metadados(pasta_metadados_origem, pasta_metadados_destino, troca_de_versao=True)

    params.DATABASEFB = '/home/base/dados.fdb'
    params.HOSTFB = 'maxsuportsistemas.com'
    params.USERFB = 'SYSDBA'
    params.PASSFB = 'masterkey'
    params.PATHDLL = verifica_dll_firebird()
    inicializa_conexao_firebird()

    try:
        executar_scripts_meta(scripts, params.FIREBIRD_CONNECTION)
    except Exception as e:
        print_log(f"Não foi possível atualizar bando master -> motivo: {e}")
    

if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            atualiza_banco()
        except Exception as e:
            print_log(f"Não foi possível executar atualização do banco master -> motivo: {e}")
        finally:
            remover_bloqueio(nome_script)