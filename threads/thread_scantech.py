import os
import sys
import base64
import requests
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes import print_log, carregar_configuracoes, inicializa_conexao_mysql


nome_servico = 'thread_scantech'
cnpj = ''
backEndVersion = "1.11.0.0"
pdvVersion = "1.11.0.0"

def converte_base_64():
    try:
        str_autenticacao = f"{parametros.USUARIOSCANTECH}:{parametros.SENHASCANTECH}"
        dados = str_autenticacao.encode("utf-8")
        str_autenticacao_base64 = base64.b64encode(dados).decode("utf-8")
        return f"Basic {str_autenticacao_base64}"
    except Exception as ex:
        return "Erro"

def salva_promocoes(promocoes, codigo_empresa, ativo):
    try:
        cursor = parametros.MYSQL_CONNECTION.cursor()
        print_log('Encontrei promoções' )

        for promocao in promocoes['results']:
            # Verifica se a promoção já existe no banco
            cursor.execute("SELECT COUNT(*) FROM PROMOCOES WHERE CODIGO = %s", (promocao['id'],))
            existe = cursor.fetchone()[0]

            # Extração dos campos necessários
            codigo = promocao['id']
            titulo = promocao['titulo']
            descricao = promocao['descripcion']
            tipo = promocao['tipo']
            quantidade_total = promocao['detalles']['condiciones']['items'][0]['cantidad']
            paga = promocao['detalles'].get('paga', None)           
            preco = promocao['detalles'].get('precio', None)
            desconto = promocao['detalles'].get('descuento', None)
            vigencia_desde = promocao['vigenciaDesde'].split('T')[0]
            vigencia_hasta = promocao['vigenciaHasta'].split('T')[0]
            limite_ticket = promocao['limitePromocionesPorTicket']

            if existe > 0:
                print_log('Atualizando a promoção ' + str(codigo))
                # Atualiza promoção existente
                cursor.execute("""
                    UPDATE PROMOCOES
                    SET TITULO = %s, DESCRICAO = %s, LIMITETICKET = %s, TIPO = %s, QUANTIDADE_TOTAL = %s, PAGA = %s, VIGENCIA_DESDE = %s, VIGENCIA_HASTA = %s, CNPJ_EMPRESA = %s, ATIVO =%s
                    WHERE CODIGO = %s
                """, (titulo, descricao, limite_ticket, tipo, quantidade_total, paga, vigencia_desde, vigencia_hasta, cnpj, codigo, ativo))
            else:
                print_log('Inserindo a promoção ' + str(codigo))
                # Insere nova promoção
                cursor.execute("""
                    INSERT INTO PROMOCOES (CODIGO, CODIGO_EMPRESA, TITULO, DESCRICAO, LIMITETICKET, TIPO, QUANTIDADE_TOTAL, PAGA, VIGENCIA_DESDE, VIGENCIA_HASTA, CNPJ_EMPRESA,ATIVO)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (codigo, codigo_empresa, titulo, descricao, limite_ticket, tipo, quantidade_total, paga, vigencia_desde, vigencia_hasta, cnpj, ativo))

            if ativo == 1:
                # Insere ou atualiza produtos da promoção
                print_log('Adicionando os produtos da promoção')
                for item in promocao['detalles']['condiciones']['items']:
                    quantidade_item = item['cantidad']
                    for produto in item['articulos']:
                        codigo_barras = produto['codigoBarras']
                        nome = produto['nombre']

                        cursor.execute("SELECT COUNT(*) FROM PRODUTO_PROMOCOES WHERE CODIGO_PROMOCAO = %s AND CODIGO_BARRAS = %s", (codigo, codigo_barras))
                        produto_existe = cursor.fetchone()[0]
                        print_log('Inserindo ou atualizando o produto ' + codigo_barras + ' - ' + nome)
                        if produto_existe > 0:
                            # Atualiza produto existente
                            cursor.execute("""
                                UPDATE PRODUTO_PROMOCOES
                                SET NOME = %s, QUANTIDADE = %s, PRECO = %s, DESCONTO = %s, CNPJ_EMPRESA = %s
                                WHERE CODIGO_PROMOCAO = %s AND CODIGO_BARRAS = %s
                            """, (nome, quantidade_item, preco, desconto, cnpj, codigo, codigo_barras))
                        else:
                            # Insere novo produto
                            cursor.execute("""
                                INSERT INTO PRODUTO_PROMOCOES (CODIGO_PROMOCAO, CODIGO_BARRAS, NOME, QUANTIDADE, PRECO, DESCONTO, CNPJ_EMPRESA)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (codigo, codigo_barras, nome, quantidade_item, preco, desconto, cnpj))
                            
                # Insere ou atualiza bines da promocao        
                print_log('Adicionando os bines da promoção')
                formas_pagamento = promocao['detalles']['condiciones'].get('formasPago', [])
                if formas_pagamento:               
                    for forma in formas_pagamento:
                        descricao_forma  = forma['descripcion']
                        codigo_tipo_pgto = str(forma['codigoTipoPago'])
                        bines = forma.get('bines', [])

                        for bin_valor in bines:
                            cursor.execute("""
                                SELECT COUNT(*) FROM PROMOCOES_BINES 
                                WHERE CODIGO_PROMOCAO = %s AND CODIGO_TIPO_PGTO = %s AND BIN = %s
                            """, (codigo, codigo_tipo_pgto, bin_valor))
                            bin_existe = cursor.fetchone()[0]

                            try:
                                if bin_existe > 0:
                                    print_log(f'Atualizando BIN {bin_valor} da promoção {codigo}')
                                    cursor.execute("""
                                        UPDATE PROMOCOES_BINES
                                        SET DESCRICAO = %s
                                        WHERE CODIGO_PROMOCAO = %s AND CODIGO_TIPO_PGTO = %s AND BIN = %s
                                    """, (descricao_forma, codigo, codigo_tipo_pgto, bin_valor))
                                else:
                                    print_log(f'Inserindo BIN {bin_valor} da promoção {codigo}')
                                    cursor.execute("""
                                        INSERT INTO PROMOCOES_BINES (CODIGO_TIPO_PGTO, CODIGO_PROMOCAO, DESCRICAO, BIN, CNPJ_EMPRESA)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, (codigo_tipo_pgto, codigo, descricao_forma, bin_valor, cnpj))       
                            except Exception as e:
                                print_log(f"Erro ao salvar promoções: {e}")       
                        
        print_log('Tudo comitado')
        # Confirma as alterações no banco
        parametros.MYSQL_CONNECTION.commit()
        print_log("Promoções salvas/atualizadas com sucesso.")
    except Exception as e:
        print_log(f"Erro ao salvar promoções: {e}")
        parametros.MYSQL_CONNECTION.rollback()
    finally:
        cursor.close()
        parametros.MYSQL_CONNECTION.close()   

def consulta_promocoes_crm(estado=None):
    try:
        caminho = f"{parametros.URLBASESCANTECH}/pmkt-rest-api/v2/minoristas/{parametros.IDEMPRESASCANTECH}/locales/{parametros.IDLOCALSCANTECH}/promociones"
        if estado:
            caminho += f"?estado={estado}"

        autorizacao = converte_base_64()
        if autorizacao != "Erro":
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": autorizacao,
                "backend-version": backEndVersion,  # Substitua pela variável correspondente
                "pdv-version": pdvVersion  # Substitua pela variável correspondente                
            }
            response = requests.get(caminho, headers=headers)
            return response.json()
        else:
            return {"erro": "Autorização inválida"}
    except Exception as ex:
        print_log('Erro: ' + ex)

def envia_vendas_scantech_codigo_global(codigo_global, prefixo, foi_cancelado):
    # Formas de pagamento
    # 9 = dinheiro 
    # 10 = cartão de crédito
    # 13 = cartão de débito    
    print_log(f"Localiza venda codigo global {codigo_global}", nome_servico)

    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(f"SELECT * FROM NFCE_MASTER NM WHERE NM.CODIGO_GLOBAL = {codigo_global}")
    obj_vendas = cur_con.fetchone()
    cur_con.close()

    venda = obj_vendas
    numero_venda = venda['NUMERO']
    cancelado = foi_cancelado
    numero_venda = f"{prefixo}{venda['NUMERO']}"
    # Supondo que 'DATA_EMISSAO' e 'HORA_EMISSAO' sejam strings
    data_emissao = datetime.datetime.strptime(str(venda['DATA_EMISSAO']), '%Y-%m-%d')
    hora_emissao = datetime.datetime.strptime(str(venda['HORA_EMISSAO']), '%H:%M:%S').time()

    # Combina a data e a hora
    data_hora_emissao = datetime.datetime.combine(data_emissao, hora_emissao)
        
    # Dados principais
    dados_principais = {
        "fecha": data_hora_emissao.strftime('%Y-%m-%dT%H:%M:%S.000-0300'),
        "pagos": [],  # Será preenchido posteriormente
        "total": venda['TOTAL'],
        "numero": numero_venda,
        "detalles": [],  # Será preenchido posteriormente
        "cotizacion": 1.00,
        "cancelacion": cancelado,
        "codigoMoneda": "986",
        "recargoTotal": venda['OUTROS'],
        "descuentoTotal": venda['DESCONTO'],
        "codigoCanalVenta": 1,
        "descripcionCanalVenta": "VENDA NA LOJA"
    }
    
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(f"""SELECT * FROM VENDAS_FPG VF
                        LEFT OUTER JOIN FORMA_PAGAMENTO FP
                        ON VF.ID_FORMA = FP.CODIGO
                        WHERE VF.VENDAS_MASTER = {venda['FK_VENDA']} 
                          AND VF.CNPJ_EMPRESA = '{cnpj}' 
                          AND FP.CNPJ_EMPRESA = '{cnpj}' """)
    
    obj_formas_pagamentos = cur_con.fetchall()
    cur_con.close()        
    print_log(f"Localiza venda {venda['FK_VENDA']}", nome_servico)    

    # Constrói a lista de pagamentos com base nos resultados da consulta
    pagos = []
    for formas_pagamentos in obj_formas_pagamentos:
        if formas_pagamentos['TIPO'] == 'D': # DINHEIRO
            codigo_tipo_pagamento = 9  
        elif formas_pagamentos['TIPO'] == 'E': # DEBITO
            codigo_tipo_pagamento = 13  
        elif formas_pagamentos['TIPO'] == 'C': # CREDITO
            codigo_tipo_pagamento = 10
                
        if codigo_tipo_pagamento == 9:
            pagos.append({
                "importe": formas_pagamentos['VALOR'],
                "cotizacion": 1,
                "codigoMoneda": "986",
                "codigoTipoPago": codigo_tipo_pagamento,               
                "detalleFinalizadora": formas_pagamentos['DESCRICAO']
            })        
        else:
            numeroAuto = formas_pagamentos['CODIGOTRANSACAO']
            if len(numeroAuto) < 7:
                numeroAuto = str(numeroAuto).rjust(6,'0')
            
            
            pagos.append({
                "importe": formas_pagamentos['VALOR'],
                "cotizacion": 1,
                "codigoMoneda": "986",
                "codigoTipoPago": codigo_tipo_pagamento,                   
                "bin": formas_pagamentos['BIN_TEF'],
                "ultimosDigitosTarjeta": formas_pagamentos['ULTIMOS_DIGITOS_CARTAO_TEF'],
                "numeroAutorizacion": numeroAuto,
                "codigoTarjeta": None,#str(formas_pagamentos['BIN_TEF']),                 
                "detalleFinalizadora": formas_pagamentos['DESCRICAO']
            })             

    dados_principais["pagos"] = pagos

    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(f"SELECT * FROM NFCE_DETALHE ND LEFT OUTER JOIN PRODUTO P ON ND.ID_PRODUTO = P.CODIGO WHERE ND.FKVENDA = {venda['CODIGO']}  AND ND.CNPJ_EMPRESA = '{cnpj}' AND P.CNPJ_EMPRESA = '{cnpj}' ")
    obj_detalhes = cur_con.fetchall()
    cur_con.close()        

    # Lista de detalhes    
    detalles = []
    for detalhe in obj_detalhes:
        print_log(f"Produto {detalhe['DESCRICAO']}", nome_servico)            
        codigo_barra = detalhe['COD_BARRA']
        if not len(codigo_barra) > 7:
            codigo_barra = detalhe['CODIGO']
        detalles.append({
            "importe": detalhe['VALOR_ITEM'] - detalhe['VDESCONTO'],
            "recargo": 0,
            "cantidad": detalhe['QTD'],
            "descuento": detalhe['VDESCONTO'],
            "codigoBarras": codigo_barra,
            "codigoArticulo": detalhe['CODIGO'],
            "importeUnitario": detalhe['PRECO'],
            "descripcionArticulo": detalhe['DESCRICAO']
        })

    dados_principais["detalles"] = detalles

    url = f"http://br.homo.apipdv.scanntech.com/api-minoristas/api/v2/minoristas/{parametros.IDEMPRESASCANTECH}/locales/{parametros.IDLOCALSCANTECH}/cajas/{venda['FK_CAIXA']}/movimientos"

    autorizacao = converte_base_64()
    if autorizacao != "Erro":
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": autorizacao,        
            "backend-version": backEndVersion,  # Substitua pela variável correspondente
            "pdv-version": pdvVersion  # Substitua pela variável correspondente
        }

    try:
        print_log(f"Enviando cupom {venda['NUMERO']} da empresa {cnpj}!")
        json_data = json.dumps(dados_principais, default=lambda x: round(float(x), 2))
                    
        with open('venda.json', 'w') as j:
            json.dump(dados_principais, j, default=lambda x: round(float(x), 2))                    
                    
        response = requests.post(url, data=json_data, headers=headers)
        response.raise_for_status()

        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(f"UPDATE NFCE_MASTER SET ENVIADO_SCANTECH = 1 WHERE CODIGO = {venda['CODIGO']} AND CNPJ_EMPRESA = '{cnpj}' ")
        cur_con.close()
        parametros.MYSQL_CONNECTION.commit()
        
        if foi_cancelado:
            print_log(f"Cupom de cancelamento {venda['NUMERO']} da empresa {cnpj} enviado com sucesso!")
        else:
            print_log(f"Cupom {venda['NUMERO']} da empresa {cnpj} enviado com sucesso!")
            
    except requests.exceptions.RequestException as e:
        print_log(f"Erro enviando cupom Web Service Scanntech: {e}")    
    
def envia_vendas_scantech(CNPJEmpresa):
    # Formas de pagamento
    # 9 = dinheiro 
    # 10 = cartão de crédito
    # 13 = cartão de débito    
    print_log("Localiza vendas do ultimo dia", nome_servico)

    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    #cur_con.execute(f"SELECT * FROM NFCE_MASTER NM WHERE NM.DATA_EMISSAO BETWEEN DATE_SUB(NOW(), INTERVAL 2 DAY) AND NOW() AND SITUACAO IN ('T', 'O', 'C', 'I') AND CNPJ_EMPRESA = '{cnpj}' AND ENVIADO_SCANTECH IS NULL")

    cur_con.execute(f"SELECT * FROM NFCE_MASTER NM WHERE ENVIADO_SCANTECH = 0 AND CNPJ_EMPRESA='{CNPJEmpresa}'")
    obj_vendas = cur_con.fetchall()
    cur_con.close()

    for venda in obj_vendas:
        envia_vendas_scantech_codigo_global(venda['CODIGO_GLOBAL'],'', False)        
        
        if venda['SITUACAO'] == 'C' or venda['SITUACAO'] == 'I':
            envia_vendas_scantech_codigo_global(venda['CODIGO_GLOBAL'],'-', True)        
 
def envia_fechamento_vendas_scantech_correcao():        
    print_log("Verifica se ainda tem que mandar fechamento hoje", nome_servico)
    
    query_caixas_abertos = f"select * from CONTAS C where C.SITUACAO = 'A' AND C.CNPJ_EMPRESA = '{cnpj}' "
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(query_caixas_abertos)
    result_caixas_abertos = cur_con.fetchall()
    cur_con.close()    
    
    for caixa_aberto in result_caixas_abertos:
        # Consultas SQL
        query_vendas_liquidas = f"""
        SELECT 
            SUM(TOTAL) as vendas_liquida, 
            COUNT(CODIGO) as qtd_vendas_liquida 
        FROM NFCE_MASTER NM 
        WHERE SITUACAO IN ('T', 'O','C') 
            AND CNPJ_EMPRESA = '19775656000104' 
            AND CODIGO_GLOBAL > 457 and CODIGO_GLOBAL <=  486 """
        

        query_vendas_canceladas = f""" SELECT 
            SUM(TOTAL) as vendas_canceladas, 
            COUNT(CODIGO) as qtd_vendas_canceladas 
        FROM NFCE_MASTER NM 
        WHERE SITUACAO IN ('C') 
            AND CNPJ_EMPRESA = '19775656000104' 
            AND CODIGO_GLOBAL > 457 and CODIGO_GLOBAL <=  486
        """
        

        # Executar consultas
        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(query_vendas_liquidas)
        result_vendas_liquidas = cur_con.fetchone()
        cur_con.close()    
        
        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(query_vendas_canceladas)
        result_vendas_canceladas = cur_con.fetchone()
        cur_con.close()    
        
        valor_vendas_liquidas = result_vendas_liquidas["vendas_liquida"] or 0
        valor_vendas_canceladas = result_vendas_canceladas["vendas_canceladas"] or 0
        
        if valor_vendas_liquidas == 0 and valor_vendas_canceladas ==0:
            continue

        # Construir o JSON
        # dados_principais = {
        #     "montoVentaLiquida": valor_vendas_liquidas - valor_vendas_canceladas or 0,
        #     "montoCancelaciones": valor_vendas_canceladas or 0,
        #     "cantidadMovimientos": result_vendas_liquidas["qtd_vendas_liquida"] or 0,
        #     "fechaVentas": "2025-02-21", #datetime.datetime.now().strftime("%Y-%m-%d"),
        #     "cantidadCancelaciones": result_vendas_canceladas["qtd_vendas_canceladas"] or 0
        # }    
        
        dados_principais = {
            "montoVentaLiquida": 0,
            "montoCancelaciones":  0,
            "cantidadMovimientos": 0,
            "fechaVentas": "2025-02-25", #datetime.datetime.now().strftime("%Y-%m-%d"),
            "cantidadCancelaciones": 0
        }            

        url = f"http://br.homo.apipdv.scanntech.com/api-minoristas/api/v2/minoristas/{parametros.IDEMPRESASCANTECH}/locales/{parametros.IDLOCALSCANTECH}/cajas/3/cierresDiarios"

        autorizacao = converte_base_64()
        if autorizacao != "Erro":
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": autorizacao,
                "backend-version": backEndVersion,  # Substitua pela variável correspondente
                "pdv-version": pdvVersion  # Substitua pela variável correspondente                
            }

        try:
            print_log(f"Enviando fechamento do dia {datetime.datetime.now().strftime('%Y-%m-%d')} da empresa {cnpj}")
            json_data = json.dumps(dados_principais, default=lambda x: round(float(x), 2))
                        
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()

            data = datetime.datetime.now().strftime("%Y-%m-%d")

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f"INSERT INTO FECHAMENTOS_DIARIOS_SCANTECH (CNPJ_EMPRESA, DATA_REFERENCIA) VALUES('{cnpj}', '{data}') ")
            cur_con.close()           

            parametros.MYSQL_CONNECTION.commit()
            
            print_log(f"Enviado fechamento do dia {datetime.datetime.now().strftime('%Y-%m-%d')} da empresa {cnpj}")
        except requests.exceptions.RequestException as e:
            print_log(f"Erro enviando cupom Web Service Scanntech: {e}")
            
def efetua_promocoes():
    promocoes = consulta_promocoes_crm('ACEPTADA')
    if 'erro' not in promocoes:
       salva_promocoes(promocoes, int(oEmpresa['CODIGO']),1)
    else:
       print("Erro na consulta de promoções:", promocoes['erro'])             
    
def envia_fechamento_vendas_scantech():
    print_log("Verifica se ainda tem que mandar fechamento hoje", nome_servico)

    data = datetime.datetime.now().strftime("%Y-%m-%d")
    
    query_fechamento_diario = f"SELECT * FROM FECHAMENTOS_DIARIOS_SCANTECH WHERE DATA_REFERENCIA = '{data}' AND CNPJ_EMPRESA = '{cnpj}' "
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(query_fechamento_diario)
    result_fechamento_diario = cur_con.fetchone()
    cur_con.close()        
    
    if result_fechamento_diario:
        return

    print_log("Localiza vendas para fechamento", nome_servico)
    
    query_caixas_abertos = f"select * from CONTAS C where C.SITUACAO = 'A' AND C.CNPJ_EMPRESA = '{cnpj}' "
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(query_caixas_abertos)
    result_caixas_abertos = cur_con.fetchall()
    cur_con.close()    
    
    for caixa_aberto in result_caixas_abertos:
        # Consultas SQL
        query_vendas_liquidas = f"""
        SELECT 
            SUM(TOTAL) as vendas_liquida, 
            COUNT(CODIGO) as qtd_vendas_liquida 
        FROM NFCE_MASTER NM 
        WHERE NM.DATA_EMISSAO = CURDATE() 
            AND SITUACAO IN ('T', 'O','C') 
            AND CNPJ_EMPRESA = '{cnpj}' 
            AND ENVIADO_SCANTECH = 1
            AND FK_CAIXA = {caixa_aberto['CODIGO']}
            AND CODIGO_GLOBAL >= 22226 """
        

        query_vendas_canceladas = f""" SELECT 
            SUM(TOTAL) as vendas_canceladas, 
            COUNT(CODIGO) as qtd_vendas_canceladas 
        FROM NFCE_MASTER NM 
        WHERE NM.DATA_EMISSAO = CURDATE() 
            AND SITUACAO IN ('C') 
            AND CNPJ_EMPRESA = '{cnpj}' 
            AND ENVIADO_SCANTECH = 1
            AND FK_CAIXA = {caixa_aberto['CODIGO']}  
            AND CODIGO_GLOBAL >= 22226
        """

        # Executar consultas
        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(query_vendas_liquidas)
        result_vendas_liquidas = cur_con.fetchone()
        cur_con.close()    
        
        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(query_vendas_canceladas)
        result_vendas_canceladas = cur_con.fetchone()
        cur_con.close()    
        
        valor_vendas_liquidas = result_vendas_liquidas["vendas_liquida"] or 0
        valor_vendas_canceladas = result_vendas_canceladas["vendas_canceladas"] or 0
        
        if valor_vendas_liquidas == 0 and valor_vendas_canceladas == 0:
            continue

        # Construir o JSON
        dados_principais = {
            "montoVentaLiquida": valor_vendas_liquidas - valor_vendas_canceladas or 0,
            "montoCancelaciones": valor_vendas_canceladas or 0,
            "cantidadMovimientos": result_vendas_liquidas["qtd_vendas_liquida"] or 0,
            "fechaVentas": datetime.datetime.now().strftime("%Y-%m-%d"),
            "cantidadCancelaciones": result_vendas_canceladas["qtd_vendas_canceladas"] or 0
        }    

        url = f"http://br.homo.apipdv.scanntech.com/api-minoristas/api/v2/minoristas/{parametros.IDEMPRESASCANTECH}/locales/{parametros.IDLOCALSCANTECH}/cajas/{caixa_aberto['CODIGO']}/cierresDiarios"

        autorizacao = converte_base_64()
        if autorizacao != "Erro":
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": autorizacao,
                "backend-version": backEndVersion,  # Substitua pela variável correspondente
                "pdv-version": pdvVersion  # Substitua pela variável correspondente                
            }

        try:
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            print_log(f"Enviando fechamento do dia {data} da empresa {cnpj}")
            json_data = json.dumps(dados_principais, default=lambda x: round(float(x), 2))
                        
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f"INSERT INTO FECHAMENTOS_DIARIOS_SCANTECH (CNPJ_EMPRESA, DATA_REFERENCIA) VALUES('{cnpj}', '{data}') ")
            cur_con.close()           

            parametros.MYSQL_CONNECTION.commit()
            
            print_log(f"Enviado fechamento do dia {data} da empresa {cnpj}")
        except requests.exceptions.RequestException as e:
            print_log(f"Erro enviando cupom Web Service Scanntech: {e}")


if __name__ == "__main__":
    try:
        print_log('Iniciando serviço scantech', nome_servico)

        try:
            parametros.BASEMYSQL = 'dados'
            parametros.USERMYSQL = 'maxsuport'
            carregar_configuracoes()
            inicializa_conexao_mysql()

            print_log("Pega dados local", nome_servico)

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute('SELECT * FROM EMPRESA WHERE ATIVA_INTEGRACAO_SCANTECH = 1')
            obj_empresas = cur_con.fetchall()
            cur_con.close()

            for oEmpresa in obj_empresas:
                parametros.USUARIOSCANTECH = oEmpresa['USUARIO_SCANTECH']
                parametros.SENHASCANTECH = oEmpresa['SENHA_SCANTECH']
                parametros.IDEMPRESASCANTECH = 200381
                parametros.IDLOCALSCANTECH = 1
                parametros.URLBASESCANTECH = oEmpresa['URL_BASE_SCANTECH']
                cnpj = oEmpresa['CNPJ']

                if "fechamento" in sys.argv:
                    envia_fechamento_vendas_scantech()

                if "vendas" in sys.argv:
                    envia_vendas_scantech(cnpj)

                if "promocoes" in sys.argv:
                    efetua_promocoes()

        except Exception as e:
            if parametros.MYSQL_CONNECTION.is_connected():
                parametros.MYSQL_CONNECTION.close()
            print_log(f'Erro: {e}', nome_servico)

    except Exception as e:
        print_log(f'{e}', nome_servico)