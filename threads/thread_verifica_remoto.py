import os
import sys
import fdb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes import (
    os,
    json,
    datetime,
    print_log,
    formata_cpf,
    formata_cnpj,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    remover_caracteres,
    verifica_dll_firebird,
    inicializa_conexao_mysql,
)

def gerar_conexao(servidor='localhost', porta='3050', usuario='maxsuport', senha='oC8qUsDp', pasta_banco=''):
    con = fdb.connect(host=f'{servidor}/{porta}', user=usuario, password=senha, database=pasta_banco)
    return con

def iterar_cnpjs(cnpjs: list, con: fdb.Connection, sistema: str = 'max'):
    cursor = con.cursor()

    if sistema == 'max':
        cursor.execute('select cnpj from empresa')

    elif sistema == 'gfil':
        cursor.execute('select cnpj from diversos')

    results = cursor.fetchall()

    for result in results:
        if result[0] not in cnpjs:
            cnpjs.append(result[0])
            datahoraagora = datetime.datetime.now().replace(microsecond=0)
            if sistema == 'max':
                cursorupdate = con.cursor()  
                cursorupdate.execute(f"update empresa set ULTIMA_EXEC_SERVICO = '{datahoraagora}' where cnpj in ('{result[0]}')")     
                cursorupdate.close()   
                con.commit()    

    cursor.close()

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
                con = gerar_conexao(pasta_banco=pasta_bd)

                if con:
                    try:
                        iterar_cnpjs(cnpjs, con)
                    except Exception as e:
                        print_log(f'Erro ao verificar pastas -> motivo: {e}', nome_script)
                    finally:
                        if not con.closed:
                            con.close()

        elif 'sistemagfil' in pasta.lower():
            pasta_bd = os.path.join(pasta, 'dados', 'infolivre.fdb')

            if os.path.exists(pasta_bd):
                print_log(f'Consultando em pasta -> {pasta_bd}', nome_script)

                try:
                    con = gerar_conexao(usuario='GFILMASTER', senha='b32@m451', pasta_banco=pasta_bd)
                    if con:
                        iterar_cnpjs(cnpjs, con, 'gfil')
                except Exception as e:

                    if 'unsupported on-disk structure' in str(e):
                        print_log('Falha ao conectar, tentando em outra porta de conexao', nome_script)
                        con = gerar_conexao(porta='3040', usuario='GFILMASTER', senha='b32@m451', pasta_banco=pasta_bd)

                        if con:
                            try:
                                iterar_cnpjs(cnpjs, con, 'gfil')
                            except Exception as er:
                                print_log(f'Erro ao consultar cnpjs em segunda tentativa -> motivo: {er}', nome_script)
                    elif 'Your user name and password' in str(e):
                        continue
                    else:
                        print_log(f'Erro ao verificar pastas -> motivo: {e.__class__.__name__}:{e}', nome_script)
                finally:
                    if not con.closed:
                        con.close()

    return cnpjs

def salva_json():
    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')
    try:
        parametros.BASEMYSQL = 'dados'
        inicializa_conexao_mysql()
        
        print_log("Efetua conexão remota" , nome_servico)
        conn = parametros.MYSQL_CONNECTION
    
        print_log(f"Consultando CNPJs....." , nome_servico)
        cnpj_list = consulta_cnpj()
        cnpj = ''
        for s in cnpj_list:

            if len(s) == 11:
                s = formata_cpf(s)

            elif len(s) == 14:
                s = formata_cnpj(s)

            if (cnpj != ''):
                cnpj += ','
            cnpj += '"' + s + '"'

        # Consulta ao banco de dados
        cursor = conn.cursor(dictionary=True)
        # cursor.execute(
        #     f"""SELECT nome, cnpj, cidade, uf, ativo, sistema_ativo, sistema_em_uso_id, pasta_compartilhada_backup, 
        #             caminho_base_dados_maxsuport, caminho_gbak_firebird_maxsuport, porta_firebird_maxsuport, 
        #             caminho_base_dados_gfil,caminho_gbak_firebird_gfil,alerta_bloqueio,timer_minutos_backup, porta_firebird_gfil, 
        #             ip
        #     FROM cliente_cliente where cnpj in ({cnpj})""")
        # rows = cursor.fetchall()

        sql_select = f"""SELECT
                        P.RAZAO,
                        P.CNPJ,
                        P.MUNICIPIO,
                        P.UF,
                        P.ATIVO,
                        P.SISTEMA_EM_USO,
                        P.PASTA_COMPARTILHADA_BACKUP,
                        P.CAMINHO_BASE_DADOS,
                        P.CAMINHO_GBAK_FIREBIRD,
                        P.PORTA_FIREBIRD,
                        P.VALIDADE_SISTEMA
                    FROM
                        PESSOA P
                    WHERE
                        P.CNPJ_EMPRESA = '19775656000104'
                        AND
                        P.CNPJ in ({cnpj})"""
        
        cursor.execute(sql_select)
        rows = cursor.fetchall()

        print_log(f"Consultou remoto cnpj's {cnpj}" , nome_servico)
        conn.close()

        config = {}
        config['sistema'] = {}
        for row in rows:
            # config['sistema'][row['cnpj']] = {"sistema_ativo": str(row['sistema_ativo']),
            #                                 "alerta_bloqueio": str(row['alerta_bloqueio']),
            #                                 "sistema_em_uso_id": str(row['sistema_em_uso_id']),
            #                                 "pasta_compartilhada_backup": str(row['pasta_compartilhada_backup']),
            #                                 "caminho_base_dados_maxsuport": str(row['caminho_base_dados_maxsuport']),
            #                                 "caminho_gbak_firebird_maxsuport": str(row['caminho_gbak_firebird_maxsuport']),
            #                                 "porta_firebird_maxsuport": str(row['porta_firebird_maxsuport']),
            #                                 "caminho_base_dados_gfil": str(row['caminho_base_dados_gfil']),
            #                                 "caminho_gbak_firebird_gfil": str(row['caminho_gbak_firebird_gfil']),
            #                                 "porta_firebird_gfil": str(row['porta_firebird_gfil']),
            #                                 "timer_minutos_backup": str(row['timer_minutos_backup']),
            #                                 "ip": str(row['ip'])
            #                                 }
            config['sistema'][remover_caracteres(row['CNPJ'])] = {
                "nome": row.get('RAZAO', ''),
                "municipio": row.get('MUNICIPIO', ''),
                "uf": row.get('UF', ''),
                "sistema_ativo": '1'if row['ATIVO'] == 'S' else '0',
                "sistema_em_uso": str(row.get('SISTEMA_EM_USO', '1')),
                "pasta_compartilhada_backup": row.get('PASTA_COMPARTILHADA_BACKUP', 'C:\\BackupMaxSuport'),
                "caminho_base_dados": row.get('CAMINHO_BASE_DADOS'),
                "caminho_gbak_firebird": row.get('CAMINHO_GBAK_FIREBIRD', ''),
                "porta_firebird": str(row.get('PORTA_FIREBIRD', '3050')),
                "validade_sistema": str(row.get('VALIDADE_SISTEMA', ''))
            }
        if not os.path.exists(os.path.join(parametros.SCRIPT_PATH, 'data')):
            os.makedirs(os.path.join(parametros.SCRIPT_PATH, 'data'))
            
        with open(os.path.join(parametros.SCRIPT_PATH, 'data', 'config.json'), 'w') as configfile:            
            json.dump(config, configfile, indent=2)
        
        print_log("Arquivo config salvo com sucesso!", nome_script)

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