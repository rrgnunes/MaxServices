import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from salva_metadados_json import salva_json_metadados_local
from credenciais import parametros as params
from funcoes.funcoes import verifica_dll_firebird

def gravar():

    params.DATABASEFB = 'C:\\MaxSuport\\Dados\\Dados.fdb'
    params.PATHDLL = verifica_dll_firebird()
    caminho_destino = os.path.abspath(os.path.join(__file__, '..', 'metadados_local', 'data'))

    salva_json_metadados_local(params.DATABASEFB, caminho_destino)


if __name__ == '__main__':

    gravar()