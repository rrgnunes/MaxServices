from logging.handlers import RotatingFileHandler
import fdb
import psutil
import os
import sys
import parametros
from funcoes import (
    print_log, exibe_alerta,
    inicializa_conexao_mysql,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    crypt,
    carrega_arquivo_config,
    inicializa_conexao_firebird
    )

def verifica_dados_local():
    nome_servico = 'thread_bloqueio'
    try:
        inicializa_conexao_mysql()
        carrega_arquivo_config()
        print_log("Pegando dados locais", nome_servico)
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo']
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']

            print_log(f"Local valor {ativo} do CNPJ {cnpj}", nome_servico)

            if ativo == "0" and sistema_em_uso == "2":
                caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil'].replace('\\', '/')
                caminho_base_dados_gfil = caminho_base_dados_gfil.split('/')[0] + '/' + caminho_base_dados_gfil.split('/')[1]
                print_log("Encerra Processo do GFIL", nome_servico)
                for proc in psutil.process_iter(['name', 'exe']):
                    if 'GerenciadorFIL' in proc.info['name']:
                        if caminho_base_dados_gfil in proc.info['exe'].replace('\\', '/'):
                            print_log(f"Encerra Processo do GFIL na proc {caminho_base_dados_gfil}, no caminho {proc.info['exe']}", nome_servico)
                            proc.kill()
                            print_log("Iniciar conexão com alerta", nome_servico)
                            exibe_alerta()

            if sistema_em_uso == "1":
                data_cripto = '80E854C4A6929988F97AE2'
                if ativo == "1":
                    try:
                        conn = parametros.MYSQL_CONNECTION
                        # Consulta ao banco de dados
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute(f"""select cc.validade_sistema  from cliente_cliente cc  where cnpj in ({cnpj})""")
                        rows = cursor.fetchall()[0]
                        data_cripto = crypt('C', rows['validade_sistema'])
                        if not data_cripto:
                            data_cripto = '80E854C4A6929988F879E1'
                    finally:
                        if cursor:
                            cursor.close()

                try:
                    parametros.DATABASEFB = dados_cnpj['caminho_base_dados_maxsuport']
                    if (parametros.DATABASEFB == None) or (parametros.DATABASEFB == 'None'):
                        print_log('Banco não definido...', nome_servico)
                        continue
                    parametros.PATHDLL = os.path.join(dados_cnpj['caminho_gbak_firebird_maxsuport'], 'fbclient.dll')
                    # inicializa_conexao_firebird(os.path.join(dados_cnpj['caminho_gbak_firebird_maxsuport'], 'fbclient.dll'))
                    inicializa_conexao_firebird()
                    con = parametros.FIREBIRD_CONNECTION
                    cur = con.cursor()
                    comando = 'Liberar' if ativo == "1" else 'Bloquear'
                    print_log(f"Comando para {comando} maxsuport", nome_servico)
                    cur.execute(f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}'")
                    con.commit()
                    cur.close()
                    con.close()
                    parametros.FIREBIRD_CONNECTION = None
                except Exception as e:
                    print_log(f"Erro ao executar consulta: {e}", nome_servico)
    except Exception as e:
        print_log(f"Erro: {e}", nome_servico)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            verifica_dados_local()
        except Exception as e:
            print(f'Ocorreu um erro ao executar - motivo:{e}')
        finally:
            remover_bloqueio(nome_script)