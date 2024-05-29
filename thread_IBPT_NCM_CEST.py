from funcoes import print_log
import fdb
import mysql.connector
import os
import json
import datetime
import threading
import csv
from parametros import MYSQL_CONNECTION, FIREBIRD_CONNECTION, CNPJ_CONFIG, HOSTMYSQL, USERMYSQL, PASSMYSQL, BASEMYSQL, USERFB, PASSFB

class threadIBPTNCMCEST(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.IBPTNCMCEST()

    def IBPTNCMCEST(self):
        print_log("Carrega configurações da thread", "IBPTNCMCEST")
        
        while not self.event.wait(2):
            try:
                print_log("Pega dados local", "IBPTNCMCEST")
                for cnpj, dados_cnpj in CNPJ_CONFIG['sistema'].items():
                    ativo = dados_cnpj['sistema_ativo'] == '1'
                    sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                    caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                    caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
                    porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']

                    if ativo:
                        conMYSQL = MYSQL_CONNECTION
                        if conMYSQL.is_connected():
                            print_log("Banco MySQL conectado", "IBPTNCMCEST")
                            if sistema_em_uso == '1':  # maxsuport
                                if caminho_base_dados_maxsuport and caminho_gbak_firebird_maxsuport and porta_firebird_maxsuport:
                                    fdb.load_api(f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll')
                                    conFirebird = FIREBIRD_CONNECTION

                                    cursorMYSQL = conMYSQL.cursor(dictionary=True)
                                    cursorFirebird = conFirebird.cursor()

                                    cursorMYSQL.execute("SELECT * FROM ibpt_ibpt WHERE ESTADO = 'MT'")
                                    result_remoto = cursorMYSQL.fetchone()
                                    sVersaoRemota = result_remoto['versao']

                                    resultados = cursorMYSQL.fetchall()

                                    # Salva os dados em um arquivo CSV
                                    with open('resultados.csv', mode='w', encoding='utf-8', newline='') as f:
                                        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                                        writer.writeheader()
                                        writer.writerows(resultados)

                                    print_log("Dados salvos em resultados.csv", "IBPTNCMCEST")

                                    cursorFirebird.execute("SELECT * FROM IBPT WHERE VERSAO = ?", (sVersaoRemota,))
                                    result_local = cursorFirebird.fetchone()
                                    sVersaoLocal = result_local[12] if result_local else None

                                    dia = datetime.datetime.now().day

                                    if sVersaoRemota != sVersaoLocal and dia in [2, 4, 6, 20]:
                                        print_log("Versão remota diferente da versão local, iniciando atualização", "IBPTNCMCEST")

                                        cursorFirebird.execute("DELETE FROM IBPT")
                                        conFirebird.commit()
                                        print_log("Tabela IBPT local limpa", "IBPTNCMCEST")

                                        contagem = 0

                                        for row in cursorMYSQL:
                                            cursorFirebird.execute("""
                                                INSERT INTO IBPT (
                                                    CODIGO, EX, TIPO, DESCRICAO, NACIONALFEDERAL, IMPORTADOSFEDERAL, 
                                                    ESTADUAL, MUNICIPAL, VIGENCIAINICIO, VIGENCIAFIM, CHAVE, VERSAO, FONTE
                                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                            """, (
                                                row['codigo'], row['ex'], row['tipo'], row['descricao'][:250], row['nacional_federal'], 
                                                row['importados_federal'], row['estadual'], row['municipal'], row['vigencia_inicio'], 
                                                row['vigencia_fim'], row['chave'], row['versao'], row['fonte']
                                            ))
                                            contagem += 1
                                            if contagem % 25 == 0:
                                                print_log(f"{contagem} registros inseridos na tabela IBPT local", "IBPTNCMCEST")
                                        conFirebird.commit()

                                        print_log(f"Total de {contagem} registros inseridos na tabela IBPT local", "IBPTNCMCEST")
                                        self.atualiza_ncm_cest(conFirebird, conMYSQL)

                                        print_log("Atualizando tabela IBPT (NCMs), por favor aguarde...", "IBPTNCMCEST")
                                        cursorFirebird.execute("UPDATE PRODUTO SET CEST = '' WHERE ncm <> '' AND ncm <> '00000000'")
                                        conFirebird.commit()
                                        print_log("Tabela IBPT (NCMs) atualizada", "IBPTNCMCEST")

            except Exception as a:
                if conMYSQL.is_connected():
                    conMYSQL.rollback()
                if conFirebird:
                    conFirebird.rollback()
                print_log(f"Erro: {a}", "IBPTNCMCEST")
            finally:
                if conMYSQL.is_connected():
                    conMYSQL.close()
                if conFirebird:
                    conFirebird.close()

    def atualiza_ncm_cest(self, conFirebird, conMYSQL):
        try:
            cursorMYSQL = conMYSQL.cursor(dictionary=True)
            cursorFirebird = conFirebird.cursor()

            print_log("Iniciando atualização de NCMCEST", "IBPTNCMCEST")

            # Seleciona todos os registros da tabela NCMCEST no banco remoto
            cursorMYSQL.execute("SELECT * FROM ibpt_ncmcest")
            result_remoto = cursorMYSQL.fetchall()

            # Limpa a tabela NCMCEST no banco local
            cursorFirebird.execute("DELETE FROM NCMCEST")
            conFirebird.commit()
            print_log("Tabela NCMCEST local limpa", "IBPTNCMCEST")

            contagem = 0
            # Insere os registros do banco remoto no banco local
            for row in result_remoto:
                cursorFirebird.execute("""
                    INSERT INTO NCMCEST (NCM, CEST) VALUES (?, ?)
                """, (row['ncm'], row['cest']))
                contagem += 1
                if contagem % 25 == 0:
                    print_log(f"{contagem} registros inseridos na tabela NCMCEST local", "IBPTNCMCEST")
            conFirebird.commit()

            print_log(f"Total de {contagem} registros inseridos na tabela NCMCEST local", "IBPTNCMCEST")

        except Exception as e:
            if conMYSQL.is_connected():
                conMYSQL.rollback()
            if conFirebird:
                conFirebird.rollback()
            print_log(f"Erro: {e}", "IBPTNCMCEST")

        finally:
            cursorMYSQL.close()
            cursorFirebird.close()
