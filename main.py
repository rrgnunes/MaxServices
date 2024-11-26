import crudIBPT
import crudNCMCEST
import pandas as pd
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import logging
import sys
import math


logging.basicConfig(handlers=[logging.FileHandler(filename="/home/dinheiro/script/log.log",
                                                  encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%F %A %T",
                    level=logging.INFO)

TOKEN = 'G9luAati0Qr-ztcQwBzBeZZfRibPdTbq-hUxdZt1sUviXKo9qxz1cI2hxLkKVzkh'


def ImportaTabelasIBPT():
    logging.info('---Inicia importação de tabelas IBPT---')
    pasta_arquivos = r'/home/dinheiro/ftp/IBPT'
    # pasta_arquivos = r'C:\Users\usuario\Documents\tabelas'
    arquivos = os.listdir(pasta_arquivos)
    valores = []
    for arquivo in arquivos:
        estado = arquivo[12:14]
        versao = arquivo[14:20]

        se_arquivo_novo = crudIBPT.select_versao_IBPT(versao, estado)
        if len(se_arquivo_novo) > 0:
            continue
        iLinha = 0
        csvreader = pd.read_csv(pasta_arquivos + '/' +
                                arquivo, encoding="ISO-8859-1", on_bad_lines='skip', delimiter=';')
        csvreader = csvreader.reset_index()
        try:
            for index, linha in csvreader.iterrows():
                try:
                    tuplaValor = (
                        str(linha['codigo']).zfill(8),
                        linha['ex'] if not math.isnan(linha['ex']) else '',
                        linha['tipo'],
                        linha['descricao'],
                        linha['nacionalfederal'],
                        linha['importadosfederal'],
                        linha['estadual'],
                        linha['municipal'],
                        linha['vigenciainicio'],
                        linha['vigenciafim'],
                        linha['chave'],
                        linha['versao'],
                        linha['fonte'],
                        estado
                    )
                    valores.append(tuplaValor)
                    iLinha += 1
                except Exception as e:
                    logging.info('---Erro ao importar tabela ---\n' + str(e))
            crudIBPT.delete_IBPT_versao_diferente(estado, versao)
        except:
            logging.info(
                '---Erro ao importar tabela na linha ' + str(iLinha) + ' ---')

    crudIBPT.insert_IBPT(valores)
    logging.info('---Finaliza importação de tabelas IBPT---')


def AtualizaCEST():
    logging.info('---Inicia Atualização dos CEST''s---')

    tabela_ncm = crudIBPT.select_distinct_IBPT(estado='MT')
    i = 1
    for item_ncm in tabela_ncm:
        time.sleep(1)
        if i % 100 == 0:
            logging.info('---Enviados ' + str(i) + ' CEST''s---')
        html = urlopen(
            "http://www.buscacest.com.br/?ncm=" + item_ncm[0])
        bs = BeautifulSoup(html, 'html.parser')
        botoes_cest = bs.find_all(
            'button', {'class': 'btn btn-default use-cest'})
        for botao_cest in botoes_cest:
            cest = botoes_cest[0]['cest']
            tuplaValor = (item_ncm[0], cest)
            valores = []
            valores.append(tuplaValor)
            crudNCMCEST.insert_NCMCEST(valores)
            logging.info('---Inserido CEST ' + cest +
                         ' no NCM ' + item_ncm[0] + '---')
        i += 1
    logging.info('---Finaliza Atualização dos CEST''s---')


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[0] == 'IBPT':
        ImportaTabelasIBPT()
    if args[0] == 'NCMCEST':
        AtualizaCEST()
