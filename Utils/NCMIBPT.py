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
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from credenciais import parametros

logging.basicConfig(handlers=[logging.FileHandler(filename="logibpt.log",
                                                  encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%F %A %T",
                    level=logging.INFO)

def ImportaTabelasIBPT():
    import os, logging, pandas as pd

    def nz(s):
        return ("" if s is None else str(s)).strip()

    def norm_num(s):
        s = nz(s)
        if s == "":
            return None
        return s.replace(",", ".")

    def scalarize(v):
        # evita tuple/list/dict indo pro DB
        if isinstance(v, (tuple, list, dict)):
            return str(v)
        return v

    print('---Inicia importação de tabelas IBPT---')
    logging.info('---Inicia importação de tabelas IBPT---')

    pasta_arquivos = os.path.join(parametros.SCRIPT_PATH, "utils/lista_ibpt")
    arquivos = os.listdir(pasta_arquivos)

    for arquivo in arquivos:
        try:
            estado = arquivo[12:14]
            versao = arquivo[14:20]

            if crudIBPT.select_versao_IBPT(versao, estado):
                msg = f'---Versão {versao} do estado {estado} já importada, pulando---'
                print(msg); logging.info(msg)
                continue

            df = pd.read_csv(
                os.path.join(pasta_arquivos, arquivo),
                encoding="ISO-8859-1",
                on_bad_lines='skip',
                delimiter=';',
                dtype=str,
                keep_default_na=False
            )

            crudIBPT.delete_IBPT_versao_diferente(estado, versao)

            valores = []
            iLinha = 0

            for _, linha in df.iterrows():
                try:
                    sCodigo = nz(linha.get('codigo', ''))
                    if '.' in sCodigo:
                        sCodigo = sCodigo.split('.', 1)[0]
                    sCodigo = sCodigo.zfill(8)

                    sEx     = nz(linha.get('ex', ''))
                    sTipo   = nz(linha.get('tipo', ''))
                    sVersao = nz(linha.get('versao', versao))

                    tuplaValor = (
                        scalarize(sCodigo),
                        scalarize(sEx),
                        scalarize(sTipo),
                        scalarize(nz(linha.get('descricao', ''))),
                        scalarize(norm_num(linha.get('nacionalfederal', ''))),
                        scalarize(norm_num(linha.get('importadosfederal', ''))),
                        scalarize(norm_num(linha.get('estadual', ''))),
                        scalarize(norm_num(linha.get('municipal', ''))),
                        scalarize(nz(linha.get('vigenciainicio', ''))),
                        scalarize(nz(linha.get('vigenciafim', ''))),
                        scalarize(nz(linha.get('chave', ''))),
                        scalarize(sVersao),
                        scalarize(nz(linha.get('fonte', ''))),
                        scalarize(estado),
                    )

                    valores.append(tuplaValor)
                    iLinha += 1

                except Exception as e:
                    msg = f'---Erro na linha {iLinha}: {e}---'
                    print(msg); logging.info(msg)

            # valida antes de inserir
            bad = []
            for r_idx, row in enumerate(valores):
                for c_idx, col in enumerate(row):
                    if isinstance(col, (tuple, list, dict)):
                        bad.append((r_idx, c_idx, type(col).__name__, repr(col)[:120]))
            if bad:
                for r in bad:
                    msg = f"[VALIDACAO] Valor composto detectado antes do insert -> linha {r[0]} col {r[1]} tipo {r[2]} val {r[3]}"
                    print(msg); logging.info(msg)
                # corrige tudo forçando str
                valores = [tuple(str(x) if isinstance(x, (tuple, list, dict)) else x) for x in valores]

            if valores:
                crudIBPT.insert_IBPT(valores)
                msg = f'---Arquivo {arquivo} importado: {iLinha} linhas ({estado}-{versao})---'
                print(msg); logging.info(msg)

        except Exception as e:
            msg = f'---Erro ao importar arquivo {arquivo}: {e}---'
            print(msg); logging.info(msg)

    print('---Finaliza importação de tabelas IBPT---')
    logging.info('---Finaliza importação de tabelas IBPT---')


def AtualizaCEST():
    logging.info('---Inicia Atualização dos CEST''s---')

    tabela_ncm = crudIBPT.select_distinct_IBPT(estado='MT')
    i = 1
    for item_ncm in tabela_ncm:
        time.sleep(1)
        if i % 100 == 0:
            print('---Enviados ' + str(i) + ' CEST''s---')
            logging.info('---Enviados ' + str(i) + ' CEST''s---')
        print('---Localizando NCM ' + item_ncm[0] + '---')    
        html = urlopen("http://www.buscacest.com.br/?ncm=" + item_ncm[0])
        bs = BeautifulSoup(html, 'html.parser')
        botoes_cest = bs.find_all('button', {'class': 'btn btn-default use-cest'})
        for botao_cest in botoes_cest:
            cest = botoes_cest[0]['cest']
            tuplaValor = (item_ncm[0], cest)
            valores = []
            valores.append(tuplaValor)
            crudNCMCEST.insert_NCMCEST(valores)
            print('---Inserido CEST ' + cest + ' no NCM ' + item_ncm[0] + '---')
            logging.info('---Inserido CEST ' + cest + ' no NCM ' + item_ncm[0] + '---')
        i += 1
    print('---Finaliza Atualização dos CEST''s---')
    logging.info('---Finaliza Atualização dos CEST''s---')
    
def limpa_pasta_destino(pasta):
    itens = os.listdir(pasta)
    for item in itens:
        caminho_item = os.path.join(pasta, item)
        if os.path.isfile(caminho_item):
            os.unlink(caminho_item)

def AtualizaExcelIBPT():
    # Página inicial
    url_pagina = "https://www.minf.com.br/link.php"
    base_url = "https://www.minf.com.br/baixar2.php"

    # Pasta destino
    pasta_destino = os.path.join(parametros.SCRIPT_PATH, "Utils/lista_ibpt")
    os.makedirs(pasta_destino, exist_ok=True)

    # Buscar HTML da página
    resp = requests.get(url_pagina)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    if resp.status_code != 200:
        return
    
    limpa_pasta_destino(pasta_destino)

    # Procurar links com padrão ibpt/TabelaIBPTax
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "ibpt/TabelaIBPTax" in href:
            parsed = urlparse(href)
            params = parse_qs(parsed.query)

            arquivo = params.get('arquivo', [''])[0]
            setkey  = params.get('setkey', [''])[0]

            if arquivo.endswith(".csv") and setkey:
                novo_link = f"{base_url}?arquivo={arquivo}&setkey={setkey}"
                nome_arquivo = os.path.join(pasta_destino, os.path.basename(arquivo))
                print(f"Baixando: {novo_link}")
                r = requests.get(novo_link)
                with open(nome_arquivo, 'wb') as f:
                    f.write(r.content)
                print(f"Salvo: {nome_arquivo}")

if __name__ == '__main__':
    args = sys.argv[1:]
       
    funcao = args[0]

    
    if funcao == 'IBPT':
        ImportaTabelasIBPT()
    if funcao == 'NCMCEST':
        AtualizaCEST()
    if funcao == 'EXCELIBPT':
        AtualizaExcelIBPT()
