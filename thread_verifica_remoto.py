import parametros
import os
import sys
from funcoes import print_log, os,json, datetime,inicializa_conexao_mysql, pode_executar, criar_bloqueio, remover_bloqueio


def salva_json():
    nome_servico = 'thread_verifica_remoto'
    try:
        
        inicializa_conexao_mysql()
        
        print_log("Efetua conexão remota" , nome_servico)
        conn = parametros.MYSQL_CONNECTION

        # pego dados do arquivo
        print_log(f"Carrega arquivo {parametros.SCRIPT_PATH}\\cnpj.txt" , nome_servico)
        if os.path.exists(f"{parametros.SCRIPT_PATH}\\cnpj.txt"):
            with open(f"{parametros.SCRIPT_PATH}\\cnpj.txt", 'r') as config_file:
                cnpj_list = config_file.read().split('\n')
        cnpj = ''
        for s in cnpj_list:
            if (cnpj != ''):
                cnpj += ','
            cnpj += '"' + s + '"'

        # Consulta ao banco de dados
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"""SELECT nome, cnpj, cidade, uf, ativo, sistema_ativo, sistema_em_uso_id, pasta_compartilhada_backup, 
                    caminho_base_dados_maxsuport, caminho_gbak_firebird_maxsuport, porta_firebird_maxsuport, 
                    caminho_base_dados_gfil,caminho_gbak_firebird_gfil,alerta_bloqueio,timer_minutos_backup, porta_firebird_gfil, 
                    ip
            FROM cliente_cliente where cnpj in ({cnpj})""")
        rows = cursor.fetchall()
        print_log(f"Consultou remoto cnpj's {cnpj}" , nome_servico)

        datahoraagora = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-4)))
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE cliente_cliente set ultima_conexao_windows_service = '{datahoraagora}' where cnpj in ({cnpj})")
        print_log(f"Executou update remoto" , 'verificaremoto')
        conn.commit()
        conn.close()

        config = {}
        config['sistema'] = {}
        for row in rows:
            config['sistema'][row['cnpj']] = {"sistema_ativo": str(row['sistema_ativo']),
                                            "alerta_bloqueio": str(row['alerta_bloqueio']),
                                            "sistema_em_uso_id": str(row['sistema_em_uso_id']),
                                            "pasta_compartilhada_backup": str(row['pasta_compartilhada_backup']),
                                            "caminho_base_dados_maxsuport": str(row['caminho_base_dados_maxsuport']),
                                            "caminho_gbak_firebird_maxsuport": str(row['caminho_gbak_firebird_maxsuport']),
                                            "porta_firebird_maxsuport": str(row['porta_firebird_maxsuport']),
                                            "caminho_base_dados_gfil": str(row['caminho_base_dados_gfil']),
                                            "caminho_gbak_firebird_gfil": str(row['caminho_gbak_firebird_gfil']),
                                            "porta_firebird_gfil": str(row['porta_firebird_gfil']),
                                            "timer_minutos_backup": str(row['timer_minutos_backup']),
                                            "ip": str(row['ip'])
                                            }

        with open('C:/Users/Public/config.json', 'w') as configfile:
            json.dump(config, configfile)

    except Exception as a:
        print_log(a, nome_servico)

if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            salva_json()
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar - motivo: {e}')
        finally:
            remover_bloqueio(nome_script)