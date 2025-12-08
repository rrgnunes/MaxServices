import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.model_replicador_retorno import ReplicadorRetorno
from credenciais import parametros as params
from funcoes.funcoes import (
    inicializa_conexao_mysql_replicador,
    inicializa_conexao_firebird,
    print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    caminho_bd,
    verifica_dll_firebird
    )


if __name__ == '__main__':

    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_servico):
        criar_bloqueio(nome_servico)
        try:
            banco_ini_info = caminho_bd()
            params.PATHDLL = verifica_dll_firebird()
            params.DATABASEFB = banco_ini_info[0]

            if banco_ini_info[2] == '1':
                params.BASEMYSQL_REP = 'DADOSHM'

            inicializa_conexao_firebird()
            inicializa_conexao_mysql_replicador()

            replicador = ReplicadorRetorno(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
            replicador.nome_servico = nome_servico
            replicador.replicar_alteracoes()

        except Exception as e:
            print_log(f'Não foi possível executar serviço -> motivo: {e}', nome_servico)
            
        finally:
            remover_bloqueio(nome_servico)