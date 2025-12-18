import fdb
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from utils.salva_metadados_json import salva_metadados_mysql, salva_json_metadados_local
from funcoes.funcoes import (
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    print_log,
    obter_dados_ini
)

def atualiza_banco_mysql():
    salva_metadados_mysql('DADOSHM')

    info = obter_dados_ini(os.path.join(params.SCRIPT_PATH.replace('SERVER', ''), 'banco.ini'))

    salva_json_metadados_local(info['caminho_banco'])



if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            atualiza_banco_mysql()
        except Exception as e:
            print_log(f'Não foi possível executar banco de dados mysql -> motivo: {e}')
        finally:
            remover_bloqueio(nome_script)