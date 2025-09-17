import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.model_replicador_envio import ReplicadorEnvio
from model.model_replicador_retorno import ReplicadorRetorno
from funcoes.funcoes import inicializa_conexao_firebird, inicializa_conexao_mysql_replicador
import credenciais.parametros as params

def enviar():

    replicar = ReplicadorEnvio(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
    replicar.nome_servico = 'rep_envio'
    
    # replicar.replicar_alteracoes()

def receber():
    
    replicar = ReplicadorRetorno(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
    replicar.nome_servico = 'rep_retorno'
    replicar.replicar_alteracoes()

if __name__ == '__main__' :

    # params.USERFB = 'sysdba'
    # params.PASSFB = 'masterkey'
    params.DATABASEFB = '/maxsuport/dados/dados.fdb'

    params.PATHDLL = '/fontes/maxservices/libs/fbclient64.dll'

    inicializa_conexao_firebird()
    inicializa_conexao_mysql_replicador()

    receber()