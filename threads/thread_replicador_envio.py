import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.model_replicador_envio import ReplicadorEnvio
from credenciais import parametros as params
from funcoes.funcoes import (
    print_log,
    pode_executar,
    criar_bloqueio,
    obter_dados_ini,
    remover_bloqueio,
    verifica_dll_firebird,
    carrega_arquivo_config,
    inicializa_conexao_firebird,
    inicializa_conexao_mysql_replicador,
    )


def iniciar_replicacao():

    carrega_arquivo_config()
    bancos_ja_replicados = []

    for cnpj, dados in params.CNPJ_CONFIG['sistema'].items():
        caminho_base_dados = dados['caminho_base_dados_maxsuport']
        print_log(f"Banco de dados: {caminho_base_dados}.", nome_servico)

        if caminho_base_dados in bancos_ja_replicados:
            print_log('Banco de dados ja replicado. Pulando...\n', nome_servico)
            continue

        if not os.path.exists(caminho_base_dados):
            print_log(f'Caminho da base de dados: {caminho_base_dados} não existe. Pulando...\n', nome_servico)
            continue

        caminho_sistema = caminho_base_dados.lower().replace('dados\dados.fdb', '')
        banco_ini_info = os.path.join(caminho_sistema, 'banco.ini')

        if not os.path.exists(banco_ini_info):
            print_log('Caminho de arquivo .ini não existe. Pulando...\n', nome_servico)
            continue

        info = obter_dados_ini(banco_ini_info)

        try:

            if info['ip'].lower() not in ('localhost', '127.0.0.1'):
                continue

            params.BASEMYSQL_REP = 'dados'
            if info['homologacao']:
                params.BASEMYSQL_REP = 'DADOSHM'

            params.DATABASEFB = caminho_base_dados
            params.PATHDLL = verifica_dll_firebird()
            inicializa_conexao_firebird()
            inicializa_conexao_mysql_replicador()

            replicador = ReplicadorEnvio(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
            replicador.nome_servico = nome_servico
            replicador.replicar_alteracoes()
            
            bancos_ja_replicados.append(caminho_base_dados)
        except Exception as e:
            print_log(f"Erro ao realizar replicação -> motivo: {e}", nome_servico)

        finally:
            if params.FIREBIRD_CONNECTION:
                if not params.FIREBIRD_CONNECTION.closed:
                    params.FIREBIRD_CONNECTION.close()

            if params.MYSQL_CONNECTION_REPLICADOR:
                if params.MYSQL_CONNECTION_REPLICADOR.is_connected():
                    params.MYSQL_CONNECTION_REPLICADOR.close()

            params.FIREBIRD_CONNECTION = None
            params.MYSQL_CONNECTION_REPLICADOR = None

if __name__ == '__main__':

    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_servico):
        criar_bloqueio(nome_servico)
        try:
            iniciar_replicacao()
        except Exception as e:
            print_log(f'Não foi possível iniciar replicação -> motivo: {e}', nome_servico)
        finally:
            remover_bloqueio(nome_servico)