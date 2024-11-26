import fdb
import os
import sys
import mysql.connector
import parametros
from funcoes import (
    extrair_metadados, extrair_metadados_mysql, gerar_scripts_diferentes_mysql, executar_scripts_mysql,
    print_log, inicializa_conexao_mysql_replicador, pode_executar, criar_bloqueio, remover_bloqueio
)

def atualiza_banco_mysql():
    nome_servico = 'thread_atualiza_banco_mysql'
    try:
        print_log('Verificando se precisa atualizar banco remoto', nome_servico)
        try:
            conexao_consulta = mysql.connector.connect(host=parametros.HOSTMYSQL, user=parametros.USERMYSQL, password=parametros.PASSMYSQL)
            cur_con = conexao_consulta.cursor()
            cur_con.execute('show databases')
            bds = cur_con.fetchall()
            cur_con.close()
            conexao_consulta.close()
        except Exception as e:
            if conexao_consulta.is_connected():
                conexao_consulta.close()
            print_log(f'Não foi possivel adquirir lista de banco de dados mysql: {e}', nome_servico)
            return

        try:
            fdb.load_api('C:\\Program Files\\Firebird\\Firebird_2_5\\bin\\fbclient.dll')
            server_origem = "maxsuportsistemas.com"
            port_origem = 3050
            path_origem = "/home/base/dados.fdb"
            dsn_origem = f"{server_origem}/{port_origem}:{path_origem}"
            conexao_origem_fb = fdb.connect(dsn=dsn_origem, user='SYSDBA', password='masterkey')
            print_log('Conexao firebird estabelecida com sucesso', nome_servico)
        except Exception as a:
            print_log(f'Nao foi possivel conectar em banco origem firebird: {a}', nome_servico)

        metadados_origem = extrair_metadados(conexao_origem_fb)

        for bd in bds:
            if bd[0] == 'dados':
                inicializa_conexao_mysql_replicador(bd[0])
                conexao_destino_mysql = parametros.MYSQL_CONNECTION_REPLICADOR
                metadados_destino = extrair_metadados_mysql(conexao_destino_mysql)
                scripts = gerar_scripts_diferentes_mysql(metadados_origem, metadados_destino)
                erros = executar_scripts_mysql(conexao_destino_mysql, scripts, nome_servico)
                for erro in erros:
                    print_log(f"Em banco {bd[0]} nao foi possivel executar: {erro}")

        parametros.MYSQL_CONNECTION_REPLICADOR.close()
    except Exception as e:
        print_log(f'{e}', nome_servico)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            atualiza_banco_mysql()
        except Exception as e:
            print_log(f'Ocorreu um erro na execução - motivo: {e}')
        finally:
            remover_bloqueio(nome_script)