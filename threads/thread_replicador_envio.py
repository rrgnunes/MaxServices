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
    fechar_conexao_mysql,
    fechar_conexao_firebird,
    verifica_dll_firebird,
    carrega_arquivo_config,
    inicializa_conexao_firebird,
    inicializa_conexao_mysql_replicador
    )


def iniciar_replicacao():

    carrega_arquivo_config()
    bancos_ja_replicados = []

    for cnpj, dados in params.CNPJ_CONFIG['sistema'].items():
        caminho_base_dados = dados['caminho_base_dados']
        print_log(f"Banco de dados: {caminho_base_dados}.", nome_servico)

        if caminho_base_dados in bancos_ja_replicados:
            print_log('Banco de dados ja replicado. Pulando...\n', nome_servico)
            continue

        if not caminho_base_dados or caminho_base_dados.lower() == 'none':
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
            fechar_conexao_firebird()
            fechar_conexao_mysql()

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