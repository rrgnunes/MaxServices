import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.model_replicador_retorno import ReplicadorRetorno
from credenciais import parametros as params
from funcoes.funcoes import (
    print_log,
    pode_executar,
    criar_bloqueio,
    obter_dados_ini,
    remover_bloqueio,
    verifica_dll_firebird,
    carrega_arquivo_config,
    fechar_conexao_mysql,
    fechar_conexao_firebird,
    inicializa_conexao_firebird,
    inicializa_conexao_mysql_replicador
    )

def iniciar_replicacao():
    carrega_arquivo_config()
    bancos_ja_replicados = []

    for cnpj, dados in params.CNPJ_CONFIG['sistema'].items():
        caminho_base_dados = dados['caminho_base_dados']
        print_log(f'Banco de dados: {caminho_base_dados}', nome_servico)

        if caminho_base_dados in bancos_ja_replicados:
            continue

        if (not caminho_base_dados) or (caminho_base_dados.lower() == 'none'):
            continue

        if not os.path.exists(caminho_base_dados):
            print_log(f'Banco de dados não exite, pulando...\n', nome_servico)
            continue

        caminho_sistema = caminho_base_dados.lower().replace('\dados\dados.fdb', '')
        banco_ini = os.path.join(caminho_sistema, 'banco.ini')

        if not os.path.exists(banco_ini):
            print_log(f'Arquivo banco.ini não existe, pulando...\n')
            continue

        banco_ini_info = obter_dados_ini(banco_ini)

        try:
            
            if banco_ini_info['ip'].lower() not in ('localhost', '127.0.0.1'):
                print_log(f'Pasta não é de servidor, Pulando...\n', nome_servico)
                continue

            params.BASEMYSQL_REP = 'dados'
            if banco_ini_info['homologacao']:
                params.BASEMYSQL_REP = 'DADOSHM'

            params.DATABASEFB = caminho_base_dados
            params.PATHDLL = verifica_dll_firebird()

            inicializa_conexao_firebird()
            inicializa_conexao_mysql_replicador()

            replicador = ReplicadorRetorno(params.FIREBIRD_CONNECTION, params.MYSQL_CONNECTION_REPLICADOR)
            replicador.nome_servico = nome_servico
            replicador.replicar_alteracoes()

            bancos_ja_replicados.append(caminho_base_dados)
        
        except Exception as e:
            print_log(f'Não foi possível realizar replicação do banco -> motivo: {e}', nome_servico)

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
            print_log(f'Não foi possível iniciar replicação -> motivo: {e}')
        finally:
            remover_bloqueio(nome_servico)