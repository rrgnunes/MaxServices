from funcoes import print_log,carregar_configuracoes, pode_executar, criar_bloqueio, remover_bloqueio
import fdb
import sys
import datetime
import csv
import parametros
import pathlib
import os

def IBPTNCMCEST():
    nome_servico = "thread_IBPT_NCM_CEST"
    print_log("Carrega configurações da thread", nome_servico)
    try:
        results = os.path.join(pathlib.Path(__file__).parent, 'resultados.csv')
        carregar_configuracoes()

        print_log("Pega dados local", nome_servico)
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
            caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
            porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']

            if ativo:
                conMYSQL = parametros.MYSQL_CONNECTION
                if conMYSQL.is_connected():
                    print_log("Banco MySQL conectado", nome_servico)
                    if sistema_em_uso == '1':  # maxsuport
                        if caminho_base_dados_maxsuport and caminho_gbak_firebird_maxsuport and porta_firebird_maxsuport:
                            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll')
                            conFirebird = parametros.FIREBIRD_CONNECTION

                            cursorMYSQL = conMYSQL.cursor(dictionary=True)
                            cursorFirebird = conFirebird.cursor()

                            cursorMYSQL.execute("SELECT * FROM ibpt_ibpt WHERE ESTADO = 'MT'")
                            result_remoto = cursorMYSQL.fetchone()
                            sVersaoRemota = result_remoto['versao']

                            resultados = cursorMYSQL.fetchall()

                            # Salva os dados em um arquivo CSV
                            with open(results, encoding='utf-8', mode='w', newline='') as f:
                                writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                                writer.writeheader()
                                writer.writerows(resultados)

                            print_log("Dados salvos em resultados.csv", nome_servico)

                            cursorFirebird.execute("SELECT * FROM IBPT WHERE VERSAO = ?", (sVersaoRemota,))
                            result_local = cursorFirebird.fetchone()
                            sVersaoLocal = result_local[12] if result_local else None

                            dia = datetime.datetime.now().day

                            if sVersaoRemota != sVersaoLocal and dia in [2, 4, 6, 20]:
                                print_log("Versão remota diferente da versão local, iniciando atualização", nome_servico)

                                cursorFirebird.execute("DELETE FROM IBPT")
                                conFirebird.commit()
                                print_log("Tabela IBPT local limpa", nome_servico)

                                contagem = 0

                                for row in resultados:
                                    cursorFirebird.execute("""
                                        INSERT INTO IBPT (
                                            CODIGO, EX, TIPO, DESCRICAO, NACIONALFEDERAL, IMPORTADOSFEDERAL, 
                                            ESTADUAL, MUNICIPAL, VIGENCIAINICIO, VIGENCIAFIM, CHAVE, VERSAO, FONTE
                                        ) VALUES (?, ?, ?, CAST(? AS VARCHAR(250) CHARACTER SET UTF8), ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        row['codigo'], row['ex'], row['tipo'], row['descricao'][:250].encode('utf-8'), row['nacional_federal'], 
                                        row['importados_federal'], row['estadual'], row['municipal'], row['vigencia_inicio'], 
                                        row['vigencia_fim'], row['chave'], row['versao'], row['fonte']
                                    ))
                                    contagem += 1
                                    if contagem % 25 == 0:
                                        print_log(f"{contagem} registros inseridos na tabela IBPT local", nome_servico)
                                conFirebird.commit()

                                print_log(f"Total de {contagem} registros inseridos na tabela IBPT local", nome_servico)
                                atualiza_ncm_cest(conFirebird, conMYSQL, nome_servico)

                                print_log("Atualizando tabela IBPT (NCMs), por favor aguarde...", nome_servico)
                                cursorFirebird.execute("UPDATE PRODUTO SET CEST = '' WHERE ncm <> '' AND ncm <> '00000000'")
                                conFirebird.commit()
                                print_log("Tabela IBPT (NCMs) atualizada", nome_servico)
    except Exception as a:
        if conMYSQL.is_connected():
            conMYSQL.rollback()
        if conFirebird:
            conFirebird.rollback()
        print_log(f"Erro: {a}", nome_servico)
    finally:
        if conMYSQL.is_connected():
            conMYSQL.close()
        if conFirebird:
            conFirebird.close()

def atualiza_ncm_cest(conFirebird, conMYSQL, nome_servico):
    try:
        cursorMYSQL = conMYSQL.cursor(dictionary=True)
        cursorFirebird = conFirebird.cursor()

        print_log("Iniciando atualização de NCMCEST", nome_servico)

        # Seleciona todos os registros da tabela NCMCEST no banco remoto
        cursorMYSQL.execute("SELECT * FROM ibpt_ncmcest")
        result_remoto = cursorMYSQL.fetchall()

        # Limpa a tabela NCMCEST no banco local
        cursorFirebird.execute("DELETE FROM NCMCEST")
        conFirebird.commit()
        print_log("Tabela NCMCEST local limpa", nome_servico)

        contagem = 0
        # Insere os registros do banco remoto no banco local
        for row in result_remoto:
            cursorFirebird.execute("""
                INSERT INTO NCMCEST (NCM, CEST) VALUES (?, ?)
            """, (row['ncm'], row['cest']))
            contagem += 1
            if contagem % 25 == 0:
                print_log(f"{contagem} registros inseridos na tabela NCMCEST local", nome_servico)
        conFirebird.commit()

        print_log(f"Total de {contagem} registros inseridos na tabela NCMCEST local", nome_servico)

    except Exception as e:
        if conMYSQL.is_connected():
            conMYSQL.rollback()
        if conFirebird:
            conFirebird.rollback()
        print_log(f"Erro: {e}", nome_servico)
    finally:
        cursorMYSQL.close()
        cursorFirebird.close()


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            IBPTNCMCEST()
        except Exception as e:
            print(f'Ocorreu um erro ao tentar executar - motivo: {e}')
        finally:
            remover_bloqueio(nome_script)