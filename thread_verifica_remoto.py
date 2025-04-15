import parametros
import os
import sys
import fdb
from funcoes import print_log, os,json, datetime, inicializa_conexao_mysql, pode_executar, criar_bloqueio, remover_bloqueio, verifica_dll_firebird


def consulta_cnpj():
    pasta_raiz = os.path.abspath(os.sep)
    pastas = os.listdir(pasta_raiz)
    parametros.PATHDLL = verifica_dll_firebird()
    print(parametros.PATHDLL)
    fdb.load_api(parametros.PATHDLL)
    cnpjs = []

    for pasta in pastas:
        pasta = os.path.join(pasta_raiz, pasta)

        if 'maxsuport' in pasta.lower():
            pasta_bd = os.path.join(pasta, 'dados', 'dados.fdb')

            if os.path.exists(pasta_bd):
                print_log(f'Consultando em pasta -> {pasta_bd}', nome_script)
                try:
                    con = fdb.connect(host='localhost/3050', user='sysdba', password='masterkey', database=pasta_bd)
                    cursor = con.cursor()
                    cursor.execute('select cnpj from empresa')
                    results = cursor.fetchall()
                    for result in results:
                        if result[0] not in cnpjs:
                            cnpjs.append(result[0])
                    cursor.close()
                except Exception as e:
                    print_log(f'Erro ao verificar pastas -> motivo: {e}', nome_script)
                finally:
                    con.close()
    return cnpjs

def salva_json():
    nome_servico = 'thread_verifica_remoto'
    try:
        parametros.BASEMYSQL = 'maxservices'
        inicializa_conexao_mysql()
        
        print_log("Efetua conexão remota" , nome_servico)
        conn = parametros.MYSQL_CONNECTION
    
        print_log(f"Consultando CNPJs....." , nome_servico)
        cnpj_list = consulta_cnpj()
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

        datahoraagora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
        cursor = conn.cursor()
        cursor.execute(f"UPDATE cliente_cliente set ultima_conexao_windows_service = '{datahoraagora}' where cnpj in ({cnpj})")
        print_log(f"Executou update remoto" , nome_servico)
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

        with open(f'{parametros.SCRIPT_PATH}/config.json', 'w') as configfile:
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