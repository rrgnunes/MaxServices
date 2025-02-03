import base64
import requests
import parametros
from funcoes import print_log,carregar_configuracoes,inicializa_conexao_mysql
import mysql.connector
import json
import datetime


nome_servico = 'thread_scantech'
cnpj = ''

def converte_base_64():
    try:
        str_autenticacao = f"{parametros.USUARIOSCANTECH}:{parametros.SENHASCANTECH}"
        dados = str_autenticacao.encode("utf-8")
        str_autenticacao_base64 = base64.b64encode(dados).decode("utf-8")
        return f"Basic {str_autenticacao_base64}"
    except Exception as ex:
        return "Erro"

def salva_promocoes(promocoes, codigo_empresa):
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
            vigencia_desde = promocao['vigenciaDesde'].split('T')[0]
            vigencia_hasta = promocao['vigenciaHasta'].split('T')[0]

            if existe > 0:
                print_log('Atualizando a promoção ' + str(codigo))
                # Atualiza promoção existente
                cursor.execute("""
                    UPDATE PROMOCOES
                    SET TITULO = %s, DESCRICAO = %s, TIPO = %s, QUANTIDADE_TOTAL = %s, PAGA = %s, VIGENCIA_DESDE = %s, VIGENCIA_HASTA = %s
                    WHERE CODIGO = %s
                """, (titulo, descricao, tipo, quantidade_total, paga, vigencia_desde, vigencia_hasta, codigo))
            else:
                print_log('Inserindo a promoção ' + str(codigo))
                # Insere nova promoção
                cursor.execute("""
                    INSERT INTO PROMOCOES (CODIGO, CODIGO_EMPRESA, TITULO, DESCRICAO, TIPO, QUANTIDADE_TOTAL, PAGA, VIGENCIA_DESDE, VIGENCIA_HASTA)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (codigo, codigo_empresa, titulo, descricao, tipo, quantidade_total, paga, vigencia_desde, vigencia_hasta))

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
                            SET NOME = %s, QUANTIDADE = %s
                            WHERE CODIGO_PROMOCAO = %s AND CODIGO_BARRAS = %s
                        """, (nome, quantidade_item, codigo, codigo_barras))
                    else:
                        # Insere novo produto
                        cursor.execute("""
                            INSERT INTO PRODUTO_PROMOCOES (CODIGO_PROMOCAO, CODIGO_BARRAS, NOME, QUANTIDADE)
                            VALUES (%s, %s, %s, %s)
                        """, (codigo, codigo_barras, nome, quantidade_item))
                        
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
                "Authorization": autorizacao
            }
            response = requests.get(caminho, headers=headers)
            return response.json()
        else:
            return {"erro": "Autorização inválida"}
    except Exception as ex:
        print_log('Erro: ' + ex)

def envia_vendas_scantech():
    # Formas de pagamento
    # 9 = dinheiro 
    # 10 = cartão de crédito
    # 13 = cartão de débito    
    print_log("Localiza vendas do ultimo dia", nome_servico)

    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(f"SELECT * FROM NFCE_MASTER NM WHERE NM.DATA_EMISSAO BETWEEN DATE_SUB(NOW(), INTERVAL 2 DAY) AND NOW() AND SITUACAO IN ('T', 'O', 'C', 'I') AND CNPJ_EMPRESA = '{cnpj}' AND ENVIADO_SCANTECH IS NULL")
    obj_vendas = cur_con.fetchall()
    cur_con.close()

    for venda in obj_vendas:
        sNumeroVenda = venda['NUMERO']
        cancelado = False
        if venda['SITUACAO'] == 'C' or venda['SITUACAO'] == 'I':
            cancelado = True
            sNumeroVenda = f'-{venda['NUMERO']}' 
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
            "numero": sNumeroVenda,
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
        cur_con.execute(f"SELECT * FROM VENDAS_FPG VF WHERE VF.VENDAS_MASTER = {venda['FK_VENDA']} AND CNPJ_EMPRESA = '{cnpj}' ")
        obj_formas_pagamentos = cur_con.fetchall()
        cur_con.close()        

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
                    "codigoTipoPago": codigo_tipo_pagamento
                })        
            else:
                pagos.append({
                    "importe": formas_pagamentos['VALOR'],
                    "cotizacion": 1,
                    "codigoMoneda": "986",
                    "codigoTipoPago": codigo_tipo_pagamento,                   
                    "bin": formas_pagamentos['BIN_TEF'],
                    "ultimosDigitosTarjeta": formas_pagamentos['ULTIMOS_DIGITOS_CARTAO_TEF'],
                    "numeroAutorizacion": formas_pagamentos['CODIGOTRANSACAO'],
                    "codigoTarjeta": None #formas_pagamentos['BIN_TEF'] + '**' + formas_pagamentos['ULTIMOS_DIGITOS_CARTAO_TEF']
                })             

        dados_principais["pagos"] = pagos

        cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
        cur_con.execute(f"SELECT * FROM NFCE_DETALHE ND LEFT OUTER JOIN PRODUTO P ON ND.ID_PRODUTO = P.CODIGO WHERE ND.FKVENDA = {venda['CODIGO']}  AND ND.CNPJ_EMPRESA = '{cnpj}' AND P.CNPJ_EMPRESA = '{cnpj}' ")
        obj_detalhes = cur_con.fetchall()
        cur_con.close()        

        # Lista de detalhes
        detalles = []
        for detalhe in obj_detalhes:
            detalles.append({
                "importe": detalhe['VALOR_ITEM'],
                "recargo": 0,
                "cantidad": detalhe['QTD'],
                "descuento": 0, #detalhe['VDESCONTO'],
                "codigoBarras": detalhe['COD_BARRA'],
                "codigoArticulo": detalhe['CODIGO'],
                "importeUnitario": detalhe['PRECO'],
                "descripcionArticulo": detalhe['DESCRICAO']
            })

        dados_principais["detalles"] = detalles

        url = f"http://br.homo.apipdv.scanntech.com/api-minoristas/api/v2/minoristas/{parametros.IDEMPRESASCANTECH}/locales/{parametros.IDLOCALSCANTECH}/cajas/{venda['FK_CAIXA']}/movimientos"

        autorizacao = converte_base_64()
        backEndVersion = "1.8.0.0"
        pdvVersion = "1.8.0.0"
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
                        
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f"UPDATE NFCE_MASTER SET ENVIADO_SCANTECH = 1 WHERE CODIGO = {venda['CODIGO']} AND CNPJ_EMPRESA = '{cnpj}' ")
            cur_con.close()
            parametros.MYSQL_CONNECTION.commit()
            
            print_log(f"Cupom {venda['NUMERO']} da empresa {cnpj} enviado com sucesso!")
        except requests.exceptions.RequestException as e:
            print_log(f"Erro enviando cupom Web Service Scanntech: {e}")

def envia_fechamento_vendas_scantech():
    print_log("Verifica se ainda tem que mandar fechamento hoje", nome_servico)
    
    query_fechamento_diario = f"SELECT * FROM FECHAMENTOS_DIARIOS_SCANTECH WHERE DATA_REFERENCIA = '{datetime.datetime.now().strftime("%Y-%m-%d")}' AND CNPJ_EMPRESA = '{cnpj}' "
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
    cur_con.execute(query_fechamento_diario)
    result_fechamento_diario = cur_con.fetchone()
    cur_con.close()        
    
    if result_fechamento_diario:
        return

    print_log("Localiza vendas para fechamento", nome_servico)
    
    query_caixas_abertos = f"select * from CONTAS C where C.SITUACAO = 'A' AND CNPJ_EMPRESA = '{cnpj}' "
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
            AND SITUACAO IN ('T', 'O') 
            AND CNPJ_EMPRESA = '{cnpj}' 
            AND ENVIADO_SCANTECH = 1
            AND FK_CAIXA = {caixa_aberto['CODIGO']}
        """

        query_vendas_canceladas = f"""
        SELECT 
            SUM(TOTAL) as vendas_canceladas, 
            COUNT(CODIGO) as qtd_vendas_canceladas 
        FROM NFCE_MASTER NM 
        WHERE NM.DATA_EMISSAO = CURDATE() 
            AND SITUACAO IN ('C') 
            AND CNPJ_EMPRESA = '{cnpj}' 
            AND ENVIADO_SCANTECH = 1
            AND FK_CAIXA = {caixa_aberto['CODIGO']}                
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
        dados_principais = {
            "montoVentaLiquida": result_vendas_liquidas["vendas_liquida"] or 0,
            "montoCancelaciones": result_vendas_canceladas["vendas_canceladas"] or 0,
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
                "Authorization": autorizacao
            }

        try:
            print_log(f"Enviando fechamento do dia {datetime.datetime.now().strftime("%Y-%m-%d")} da empresa {cnpj}")
            json_data = json.dumps(dados_principais, default=lambda x: round(float(x), 2))
                        
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f"INSERT INTO FECHAMENTOS_DIARIOS_SCANTECH (CNPJ_EMPRESA, DATA_REFERENCIA) VALUES('{cnpj}', '{datetime.datetime.now().strftime("%Y-%m-%d")}') ")
            cur_con.close()           

            parametros.MYSQL_CONNECTION.commit()
            
            print_log(f"Enviado fechamento do dia {datetime.datetime.now().strftime("%Y-%m-%d")} da empresa {cnpj}")
        except requests.exceptions.RequestException as e:
            print_log(f"Erro enviando cupom Web Service Scanntech: {e}")


if __name__ == "__main__":
    try:
        print_log('Iniciando serviço scantech', nome_servico)
        try:
            database = parametros.BASEMYSQL = 'dados'            
            carregar_configuracoes()
            inicializa_conexao_mysql()

            print_log("Pega dados local", nome_servico)

            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f'SELECT * FROM EMPRESA WHERE ATIVA_INTEGRACAO_SCANTECH = 1')
            obj_empresas = cur_con.fetchall()
            cur_con.close()

            for oEmpresa in obj_empresas:
                parametros.USUARIOSCANTECH = oEmpresa['USUARIO_SCANTECH']
                parametros.SENHASCANTECH = oEmpresa['SENHA_SCANTECH']
                parametros.IDEMPRESASCANTECH = 200381
                parametros.IDLOCALSCANTECH = 1
                parametros.URLBASESCANTECH = oEmpresa['URL_BASE_SCANTECH']
                cnpj = oEmpresa['CNPJ']

                #envia_fechamento_vendas_scantech()

                envia_vendas_scantech()

                #promocoes = consulta_promocoes_crm('ACEPTADA')
                #if 'erro' not in promocoes:
                #    salva_promocoes(promocoes, int(oEmpresa['CODIGO']))
                #else:
                #    print("Erro na consulta de promoções:", promocoes['erro'])             

        except Exception as e:
            if parametros.MYSQL_CONNECTION.is_connected():
                parametros.MYSQL_CONNECTION.close()
            print_log(f'Erro: {e}', nome_servico)

    except Exception as e:
        print_log(f'{e}', nome_servico)


