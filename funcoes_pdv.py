from  funcoes import print_log, selectfb, deletefb, updatefb, insertfb, numerador, gera_qr_code, obter_imagem_qrcode
import parametros

codigo_mesa_global = 0

def gera_qrcode_mesa(descricao, valor, codigo_venda, codigo_forma_pagamento, codigo_usuario):
    from datetime import datetime

    txId = gera_qr_code(descricao, valor)

    # Inserir movimento inicial no CONTAS_MOVIMENTO
    insertfb(
                    """INSERT INTO VENDAS_FPG (
            codigo, vendas_master, id_forma, valor, fk_usuario, situacao, tipo,
            codigotransacao, codigo_empresa, datapagamento, troco
            ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )""",
        [
            numerador(parametros.FIREBIRD_CONNECTION, 'VENDAS_FPG', 'CODIGO', 'N', '', ''),
            codigo_venda,
            codigo_forma_pagamento,
            float(valor),
            codigo_usuario,
            'F',
            'I',
            txId,
            1,
            datetime.now(),
            0
        ]
    )

    imgQRCode = obter_imagem_qrcode(txId)
    return imgQRCode

def fechar_venda_mesa(codigo_usuario, codigo_mesa):
    from datetime import datetime
    
    codigo_mesa_global = codigo_mesa

    mesa = selectfb(
        "SELECT CODIGO, NOME, SITUACAO FROM MESA WHERE CODIGO = ?",
        [codigo_mesa]
    )

    mesa = mesa[0]
    mesa_situacao = mesa[2]

    # 1. Verifica se cliente padrão está configurado
    cliente_padrao = selectfb(
        "SELECT CLIENTE_PADRAO, VENDEDOR_PADRAO FROM VENDAS_PARAMETROS WHERE EMPRESA = 1")
    if not cliente_padrao or not cliente_padrao[0][0]:
        print_log("Vá em configurações e informe o código do cliente Consumidor Final!")
        return

    id_cliente_padrao = cliente_padrao[0][0]
    vendedor_padrao   = cliente_padrao[0][1]

    # 2. Verifica situação da mesa
    if mesa_situacao != 'O':
        print_log("Mesa não está ocupada.")
        return
    
    consulta_caixa = selectfb(f"select CODIGO, DATA_ABERTURA, LOTE, SITUACAO from contas where id_usuario={codigo_usuario} AND SITUACAO='A'")
    if not consulta_caixa:
        return -1

    codigo_caixa = consulta_caixa[0][0];        

    # 4. Importa itens da comanda
    codigo_venda = importa_mesa_venda(codigo_usuario, 1, codigo_mesa, id_cliente_padrao, codigo_caixa)



    # 6. Verifica itens da venda
    itens = selectfb("SELECT COUNT(*) FROM VENDAS_DETALHE WHERE FKVENDA = ?", [codigo_venda])
    if not itens or itens[0][0] == 0:
        print_log("Digite os itens!")
        return

    # 7. Apaga formas de pagamento antigas
    deletefb("DELETE FROM VENDAS_FPG WHERE VENDAS_MASTER = ?", [codigo_venda])

    updatefb("UPDATE MESA SET QTD = 0, FK_MOVIMENTO = NULL, DATA = NULL, SITUACAO = 'L', IMPRESSO = 1 WHERE CODIGO = ?", [codigo_mesa])

    return codigo_venda

def cancelar_fechar_venda_mesa(codigo_venda, codigo_mesa):
    cancelado = False
    try:
        # venda_master = selectfb("SELECT TOTAL FROM VENDAS_MASTER WHERE codigo = ?", [codigo_mesa])
        # venda_master = venda_master[0]

        # updatefb("UPDATE MESA SET QTD = 0, FK_MOVIMENTO = NULL, DATA = NULL, SITUACAO = 'O', IMPRESSO = 1 WHERE CODIGO = ?", [codigo_mesa])

  
        deletefb("DELETE FROM VENDAS_MASTER WHERE CODIGO = ?", [codigo_venda])
        deletefb("DELETE FROM VENDAS_DETALHE WHERE FKVENDA = ?", [codigo_venda])


        cancelado = True
    except Exception as a:
        print_log(a,'funcoes_pdv')

    return cancelado 

def retorna_forma_pagamento():
    forma_pagamento = selectfb("SELECT CODIGO, DESCRICAO FROM FORMA_PAGAMENTO WHERE ENVIAR_APP_MESA = 1")

    if not forma_pagamento:
        print_log("Forma pagamento não configurada para mesa")
        return None
    
    return forma_pagamento

def abre_comanda():
    situacao = selectfb("SELECT SITUACAO, FK_MOVIMENTO FROM MESAS WHERE CODIGO = ?", [codigo_mesa_global])
    if not situacao:
        print_log("Mesa não encontrada ao abrir comanda.")
        return

    status_mesa, fk_movimento = situacao[0]
    param = -1 if status_mesa == 'L' else fk_movimento

    selectfb("SELECT * FROM COMANDAS_MASTER WHERE CODIGO = ?", [param])
    print_log("Comanda aberta com sucesso.")

def fechar_venda_mesa_procedimentos(codigo_mesa):
    situacao = selectfb("SELECT SITUACAO FROM MESAS WHERE CODIGO = ?", [codigo_mesa])
    if situacao and situacao[0][0] == 'L':
        print_log("Mesa já está LIVRE")
        return

    try:
        abre_tabelas()
        fecha_comandas_master(codigo_mesa)
        fecha_comanda_pessoa(codigo_mesa)
        fecha_mesa(codigo_mesa)
        abre_tabelas()
        print_log(f"Mesa {codigo_mesa} fechada com sucesso.")
    except Exception as e:
        print_log(f"Erro ao fechar a mesa: {str(e)}")
        raise

def fecha_mesa(codigo_mesa):
    updatefb(
        """UPDATE MESAS SET 
            SITUACAO = 'L', 
            FK_MOVIMENTO = NULL, 
            DATA = NULL, 
            IMPRESSO = 1 
        WHERE CODIGO = ?""",
        [codigo_mesa]
    )
    print_log(f"Mesa {codigo_mesa} marcada como LIVRE.")

def fecha_comanda_pessoa(codigo_mesa):
    pessoas = selectfb("""
        SELECT CODIGO FROM COMANDA_PESSOA 
        WHERE COMANDA = (
            SELECT CODIGO FROM COMANDAS_MASTER WHERE COD_MESA = ?
        )
    """, [codigo_mesa])

    for pessoa in pessoas:
        updatefb(
            "UPDATE COMANDA_PESSOA SET SITUACAO = 'F' WHERE CODIGO = ?",
            [pessoa[0]]
        )

    print_log("Pessoas da comanda fechadas.")

def fecha_comandas_master(codigo_mesa):
    comanda = selectfb("SELECT CODIGO FROM COMANDAS_MASTER WHERE COD_MESA = ?", [codigo_mesa])
    if not comanda:
        print_log("Comanda master não encontrada.")
        return

    updatefb("UPDATE COMANDAS_MASTER SET SITUACAO = 'F' WHERE CODIGO = ?", [comanda[0][0]])
    print_log("Comanda master fechada.")

def abre_pessoa():
    comanda = selectfb("SELECT CODIGO FROM COMANDAS_MASTER WHERE CODIGO <> -1 ORDER BY CODIGO DESC ROWS 1")
    if not comanda:
        print_log("Nenhuma comanda ativa encontrada.")
        return

    id_comanda = comanda[0][0]
    selectfb("SELECT * FROM COMANDA_PESSOA WHERE COMANDA = ?", [id_comanda])
    print_log("Pessoa da comanda carregada.")    

def abre_itens():
    pessoa = selectfb("""
        SELECT P.CODIGO, M.NOME
        FROM COMANDA_PESSOA P
        JOIN COMANDAS_MASTER C ON C.CODIGO = P.COMANDA
        JOIN MESAS M ON C.COD_MESA = M.CODIGO
        ORDER BY P.CODIGO DESC ROWS 1
    """)

    if not pessoa:
        print_log("Nenhuma pessoa ativa encontrada.")
        return

    id_pessoa = pessoa[0][0]

    # Filtro comentado no original, mantido vazio
    filtro = ''

    # Supondo que o SQL base está salvo em v_sql_item
    v_sql_item = "SELECT * FROM COMANDA_ITENS WHERE /*where*/ FK_COMANDA_PESSOA = ?"
    sql_com_filtro = v_sql_item.replace("/*where*/", filtro)

    selectfb(sql_com_filtro, [id_pessoa])
    print_log("Itens da comanda carregados.")

def abre_tabelas():
    abre_comanda()
    abre_pessoa()
    abre_itens()
    calcula_total()
    print_log("Tabelas abertas com sucesso.")    

def calcula_total():
    total = selectfb("SELECT TOTAL FROM COMANDAS_MASTER ORDER BY CODIGO DESC ROWS 1")
    if not total:
        print_log("Total da comanda não encontrado.")
        return

    valor = total[0][0] or 0
    print_log(f"Total da comanda: R$ {valor:,.2f}")

def fechar_mesa(codigo_mesa):
    situacao = selectfb("SELECT SITUACAO FROM MESAS WHERE CODIGO = ?", [codigo_mesa])
    if not situacao:
        print_log("Mesa não encontrada.")
        return

    if situacao[0][0] == 'O':
        fechar_venda_mesa_procedimentos(codigo_mesa)
    else:
        print_log("Mesa já está FECHADA.")

def insere_venda(codigo_usuario, codigo_empresa, id_cliente_padrao, codigo_caixa, total_comanda_pessoa):
    from datetime import date

    codigo_venda = numerador(parametros.FIREBIRD_CONNECTION, 'VENDAS_MASTER', 'CODIGO', 'N', '', '')

    vendedor_usuario = selectfb(f"SELECT FK_VENDEDOR FROM USUARIOS WHERE CODIGO = {codigo_usuario}")
    vendedor_usuario = vendedor_usuario[0]
    codigo_vendedor = vendedor_usuario[0]

    insertfb(
        """INSERT INTO VENDAS_MASTER (
            CODIGO, DATA_EMISSAO, DATA_SAIDA, ID_CLIENTE, FK_USUARIO, FK_CAIXA,
            FK_VENDEDOR, CPF_NOTA, SUBTOTAL, TIPO_DESCONTO, DESCONTO, TROCO,
            DINHEIRO, TOTAL, SITUACAO, FKEMPRESA, PERCENTUAL, TIPO, NECF,
            FKORCAMENTO, LOTE, GERA_FINANCEIRO, PERCENTUAL_ACRESCIMO, ACRESCIMO,
            FK_TABELA, PEDIDO, OS, FK_OS, TOTAL_TROCA, FORMA_PAGAMENTO,
            FK_ENTREGADOR, ORIGEM_VENDA, STATUSENTREGA, FLAG_NFCE
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )""",
        [
            codigo_venda,
            date.today(),
            date.today(),
            id_cliente_padrao,
            codigo_usuario,
            codigo_caixa,
            codigo_vendedor,
            '',
            total_comanda_pessoa, #subtotal
            'D',
            0,
            0,
            0,
            total_comanda_pessoa,# total
            'X',
            codigo_empresa,
            0,
            'V',
            None,
            None,
            get_lote_atual(codigo_usuario),
            'N',
            0,
            0,
            1,
            '',
            '',
            None,
            0,
            '',
            0,
            'MESAS',
            '',
            'N'
        ]
    )

    print_log(f"Nova venda criada com código: {codigo_venda}")
    return codigo_venda

def get_lote_atual(codigo_usuario):
    resultado = selectfb("""
        SELECT CODIGO, LOTE 
        FROM CONTAS 
        WHERE ID_USUARIO = ? AND SITUACAO = 'A'
    """, [codigo_usuario])

    if not resultado:
        print_log("Nenhum caixa aberto encontrado para o usuário.")
        return None

    id_caixa, lote = resultado[0]
    print_log(f"Caixa ativo: {id_caixa}, Lote: {lote}")
    return lote

def atualiza_venda(codigo_venda):
    # Marca como visualizado se ainda não estiver
    venda_info = selectfb("SELECT VISUALIZADO, SITUACAO FROM VENDAS_MASTER WHERE CODIGO = ?", [codigo_venda])
    if not venda_info:
        print_log("Venda não encontrada.")
        return

    visualizado, situacao = venda_info[0]

    if visualizado == 0:
        updatefb("UPDATE VENDAS_MASTER SET VISUALIZADO = 1 WHERE CODIGO = ?", [codigo_venda])
        print_log("Venda marcada como visualizada.")

    # Atualiza itens
    selectfb("SELECT * FROM VENDAS_DETALHE WHERE FKVENDA = ?", [codigo_venda])
    selectfb("SELECT * FROM DELIVERY_ITENS WHERE CODIGO = ?", [codigo_venda])

    # Simula atualização do grid
    print_log("Itens carregados. Situação da venda: " + situacao)

    if situacao == 'X':
        print_log("Botão de cancelar venda habilitado.")
    else:
        print_log("Botão de cancelar venda desabilitado.")

    # Calcula total (simulação)
    print_log("Total recalculado.")

def carrega_vendedor(codigo_usuario):
    resultado = selectfb(
        "SELECT VENDEDOR FROM VENDEDORCONS WHERE CODSUP = ?",
        [codigo_usuario]
    )
    
    if resultado:
        nome_vendedor = resultado[0][0]
        print_log(f"Vendedor carregado: {nome_vendedor}")
    else:
        print_log("Vendedor não encontrado.")

def finaliza_venda(codigo_venda, codigo_caixa):
    from datetime import datetime

    # Verifica se a venda existe
    dados_venda = selectfb("SELECT COUNT(*) FROM VENDAS_MASTER WHERE CODIGO = ?", [codigo_venda])
    if not dados_venda or dados_venda[0][0] == 0:
        print_log("Venda não encontrada, inserindo nova.")
        return

    # Atualiza os dados da venda
    updatefb(
        """UPDATE VENDAS_MASTER SET
            DATA_EMISSAO = ?,
            DATA_SAIDA   = ?,
            FK_CAIXA     = ?,
            LOTE         = ?,
            SITUACAO     = 'F'
        WHERE CODIGO = ?""",
        [
            datetime.now(),
            datetime.now(),
            codigo_caixa,
            get_lote_atual(),  # deve ser uma função que retorna o lote atual
            codigo_venda
        ]
    )

    print_log(f"Venda {codigo_venda} finalizada com sucesso.")

def importa_mesa_venda(codigo_usuario, codigo_empresa, codigo_mesa, id_cliente_padrao, codigo_caixa):
    mesa = selectfb(
        "SELECT CODIGO, FK_MOVIMENTO FROM MESA WHERE CODIGO = ?",
        [codigo_mesa]
    )
    mesa = mesa[0]
    
    comanda = mesa[1]
    mesa = mesa[0]

    # Carrega pessoas da comanda
    dados_pessoa = selectfb(
        "SELECT CODIGO, TOTAL FROM COMANDA_PESSOA WHERE FK_COMANDA = ?",
        [comanda]
    )
    total_comanda_pessoa = dados_pessoa[0][1]

    if not dados_pessoa:
        print_log("Pessoa da comanda não encontrada!")
        return

    codigo_pessoa = dados_pessoa[0][0]

    # Busca itens da comanda
    itens = selectfb("SELECT FK_PRODUTO, QTD, PRECO FROM COMANDA_ITENS WHERE FK_COMANDA_PESSOA = ?", [codigo_pessoa])
    if not itens:
        print_log("Nenhum item para importar.")
        return

    # Gera nova venda
    codigo_venda = insere_venda(codigo_usuario, codigo_empresa, id_cliente_padrao, codigo_caixa, total_comanda_pessoa)

    item_num = 1

    for prod in itens:
        produto = selectfb("SELECT UNIDADE, CODBARRA FROM PRODUTO WHERE CODIGO = ?", [prod[0]])
        unidade = produto[0][0] if produto else 'UN'
        codbarra = produto[0][1] if produto else ''

        insertfb(
            """INSERT INTO VENDAS_DETALHE (
                CODIGO, ID_PRODUTO, FKVENDA, ITEM, QTD, UNIDADE, PRECO, VALOR_ITEM,
                COD_BARRA, TOTAL
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )""",
            [
                numerador(parametros.FIREBIRD_CONNECTION, 'VENDAS_DETALHE', 'CODIGO', 'N', '', ''),
                prod[0],
                codigo_venda,
                item_num,
                prod[1],
                unidade,
                prod[2],
                prod[1] * prod[2],
                codbarra,
                prod[1] * prod[2]
            ]
        )
        item_num += 1    

    return codigo_venda

def abre_pdv(codigo_usuario, valor_inicial):
    from datetime import date

    try:
        if valor_inicial is None or str(valor_inicial).strip() == '':
            valor_inicial = 0

        # Primeiro verifica se já existe caixa aberto
        caixa_aberto = selectfb(f"select CODIGO, DATA_ABERTURA, LOTE, SITUACAO from contas where id_usuario={codigo_usuario} AND SITUACAO='A'")

        if caixa_aberto:
            lote = caixa_aberto[0][1]
            print_log(f"Caixa {caixa_aberto[0][0]} já está aberto com lote {lote}.")
            return lote

        # Se não existe, gera novo lote
        resultado = selectfb("SELECT MAX(LOTE) FROM CONTAS_MOVIMENTO")
        novo_lote = (resultado[0][0] or 0) + 1

        # Atualiza CONTAS para abrir o caixa
        updatefb(
            """UPDATE CONTAS SET 
                DATA_ABERTURA = CURRENT_DATE,
                SITUACAO = 'A',
                LOTE = ?,
                ID_USUARIO = ?
            WHERE CODIGO = ?""",
            [novo_lote, codigo_usuario, codigo_caixa]
        )

        print_log(f"Caixa {codigo_caixa} iniciado com lote {novo_lote}.")

        # Inserir movimento inicial no CONTAS_MOVIMENTO
        insertfb(
            """INSERT INTO CONTAS_MOVIMENTO (
                ID_CONTA_CAIXA, HISTORICO, DATA, HORA, ENTRADA, SAIDA, FKVENDA, LOTE, ID_USUARIO
            ) VALUES (?, ?, ?, CURRENT_TIME, ?, 0, 0, ?, ?)""",
            [
                codigo_caixa,
                'ABERTURA DE CAIXA',
                date.today(),
                float(valor_inicial),
                novo_lote,
                codigo_usuario
            ]
        )

        print_log("Movimento de abertura lançado.")
        return novo_lote

    except Exception as e:
        raise Exception(f"Erro ao abrir caixa: {str(e)}")
