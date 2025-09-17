import os
import re
import sys
import mysql.connector
from mysql.connector import Error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.model_replicador_envio import ReplicadorEnvio
from credenciais import parametros as params
from funcoes.funcoes import (
    inicializa_conexao_mysql_replicador,
    inicializa_conexao_firebird,
    verifica_dll_firebird,
    caminho_bd,
    print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio
    )


if __name__ == '__main__':

    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_servico):
        criar_bloqueio(nome_servico)
        try:
            params.PATHDLL = verifica_dll_firebird()
            params.DATABASEFB = caminho_bd()[0]

            inicializa_conexao_firebird()
            inicializa_conexao_mysql_replicador()

            rep = ReplicadorEnvio(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
            rep.nome_servico = nome_servico
            rep.replicar_alteracoes()
            
        except Exception as e:
            print_log(f'Não foi possível executar serviço -> motivo: [{e.__class__.__name__}] : {e}', nome_servico)
        finally:
            remover_bloqueio(nome_servico)