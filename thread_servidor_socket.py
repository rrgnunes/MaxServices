import socket
import threading
import json
import fdb
import parametros
import base64
import time
import win32print
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
from funcoes_pdv import fechar_venda_mesa,cancelar_fechar_venda_mesa,gera_qrcode_mesa
from funcoes import print_log, carregar_configuracoes, exibe_alerta, configurar_pos_printer, selectfb, updatefb, obter_nome_terminal, get_local_ip, gera_qr_code,consultar_cobranca

lImprimeGrupo = False


def handle_client_connection(client_socket):
    """
    Função para tratar a conexão com cada cliente em uma thread separada.
    """
    
    try:
        with client_socket as conn:
            while True:
                dados = conn.recv(1024)
                if not dados:
                    break
                request = dados.decode('utf-8')
                sTipo = request[0]

                if sTipo == '1':
                    mensagem = request[1:]
                    mostrar_alerta(mensagem)
                    send_response(conn, '200')
                elif sTipo == '2':
                    mensagem = request[1:]
                    #mostrar_bandeja(mensagem)
                    send_response(conn, '200')
                # elif sTipo == '3':
                #     comando_sql = request[1:]
                #     resultado = consultar_sqlite(comando_sql)
                #     resposta = json.dumps(resultado)
                #     send_response(conn, resposta)
                elif sTipo == '4':
                    valores = request[1:]
                    sMesa, sEmpresa, sTipoImpressao = valores.split('&')
                    sTipoImpressao = sTipoImpressao.split(';')[0]
                    if sTipoImpressao == 'ResumoPedido':
                        if lImprimeGrupo:
                            # efetua_impressao_por_grupo(sMesa, sEmpresa)
                            imp_pedido_grupo(sMesa, sEmpresa)
                        else:
                            # efetua_impressao_comanda(sMesa, sEmpresa)
                            imprime_consumo_mesa(sMesa, sEmpresa)
                    elif sTipoImpressao == 'ResumoMesa':
                        #efetua_impressao_resumo_mesa(sMesa, sEmpresa)
                        imprime_pedido_mesa(sMesa, sEmpresa)
                    send_response(conn, '200')
                elif sTipo == '5': # select
                    comando_sql = request[1:].split(';')[0]
                    print_log(comando_sql)
                    resultado = consulta_completa(comando_sql)
                    send_response(conn, resultado)
                elif sTipo == '6': # fecha mesa
                    valores = request[1:]
                    codigo_usuario, codigo_mesa = valores.split('&')                    
                    resultado = fechar_venda_mesa(int(codigo_usuario), int(codigo_mesa.split(';')[0]))
                    send_response(conn, str(resultado))          
                elif sTipo == '7': # cancelar FPG
                    valores = request[1:]
                    codigo_venda, codigo_mesa = valores.split('&')       
                    resultado = cancelar_fechar_venda_mesa(int(codigo_venda), int(codigo_mesa.split(';')[0]))
                    send_response(conn, str(resultado))     
                elif sTipo == '8':
                    valores = request[1:]
                    descricao, valor, codigo_venda, codigo_forma_pagamento,codigo_usuario, acao = valores.split('&')
                    acao = acao.split(';')[0]
                    
                    if acao == 'GerarQRCode':
                        imgQRCode = gera_qrcode_mesa(descricao, valor, codigo_venda, codigo_forma_pagamento, codigo_usuario)
                        send_response_bytes(conn, imgQRCode)   
                    elif acao == 'ConsultaQRCodeTxId':
                        resultado = consultar_cobranca(valor)  
                        send_response(conn, str(resultado))  

                                     

    except Exception as e:
        print_log(f"Erro ao tratar a conexão do cliente: {e}", "servidor_socket")

def servidor_socket():
    global lImprimeGrupo

    print_log("Carrega configurações", "servidor_socket")
    host = get_local_ip()  # Obtém o IP local da máquina
    port = 50001           
    try:
        print_log("Pega dados local", "servidor_socket")

        if host == '192.168.10.115':
            parametros.HOSTFB = '192.168.10.242'

        carregar_configuracoes()

        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
            caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
            porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
            path_fbclient = f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll'

            sql = f'SELECT IMPRESSAO_GRUPO FROM EMPRESA WHERE CNPJ = {cnpj}'

            resultado_empresa = selectfb(sql)

            if not resultado_empresa:
                resultado_empresa = [(None,)]

            lImprimeGrupo = resultado_empresa[0][0] == 1

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print_log(f"Servidor escutando em {host}:{port}", "servidor_socket")
            
            while True:
                conn, addr = s.accept()
                print_log(f"Conectado por {addr}", "servidor_socket")
                client_thread = threading.Thread(target=handle_client_connection, args=(conn,))
                client_thread.start()
    except Exception as e:
        print_log(f"Erro no servidor: {e}", "servidor_socket")

def consulta_completa(comando_sql):

    def json_serial(obj):
        """Função auxiliar para serializar objetos datetime, date e Decimal em strings."""
        if isinstance(obj, (datetime, date)):
            return obj.strftime("%d/%m/%Y %H:%M:%S") if isinstance(obj, datetime) else obj.strftime("%d/%m/%Y")
        elif isinstance(obj, Decimal):
            return str(obj).replace('.', ',')
        elif isinstance(obj, fdb.fbcore.BlobReader):
            return base64.b64encode(obj.read()).decode('utf-8')
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')                           
        else:
            if obj is None:
                return ''
            else:
                return obj

    try:
        # Configuração da transação serializable
        tpb = fdb.TPB()
        tpb.access_mode = fdb.isc_tpb_write
        tpb.isolation_level = fdb.isc_tpb_concurrency
        tpb.lock_resolution = fdb.isc_tpb_wait

        # Inicia a transação com o TPB
        transacao = parametros.FIREBIRD_CONNECTION.trans()
        transacao.begin(tpb=tpb.render())
        cursor = transacao.cursor()        

        if comando_sql.strip().upper().startswith('SELECT'):
            cursor.execute(comando_sql)
            rows = cursor.fetchall()
            resultado = [
                {cursor.description[i][0]: json_serial(value) for i, value in enumerate(row)}
                for row in rows
            ]
            transacao.commit()
            return json.dumps(resultado)
        else:
            cursor.execute(comando_sql)
            transacao.commit()
            return '200'
    except fdb.fbcore.DatabaseError as e:
        erro_msg = f"Erro no Banco de Dados: {e}"
        print_log(erro_msg, "servidor_socket")
        transacao.rollback()
        return json.dumps({'erro': erro_msg})
    except Exception as e:
        erro_msg = f"Erro ao executar comando SQL: {e}"
        print_log(erro_msg, "servidor_socket")
        transacao.rollback()
        return json.dumps({'erro': erro_msg})

def send_response_bytes(conn, response_bytes):
    tamanho = len(response_bytes).to_bytes(4, 'big')
    conn.sendall(tamanho + response_bytes)

def send_response(conn, response):
    response += '\n'
    response_bytes = response.encode('utf-8')
    conn.sendall(response_bytes)

def mostrar_alerta(mensagem):
    exibe_alerta(mensagem)

def imp_pedido_grupo(mesa, empresa):
    aMesas = selectfb(f"SELECT FK_MOVIMENTO FROM MESA WHERE CODIGO = {mesa}")
    aComanda = selectfb(f"SELECT CODIGO FROM COMANDA_PESSOA WHERE FK_COMANDA = {aMesas[0][0]}")

    codigo_pessoa = aComanda[0][0]

    aItens = selectfb("""
        SELECT im.codigo, gr.descricao
        FROM comanda_itens ci
        LEFT JOIN produto pr ON ci.FK_PRODUTO = pr.CODIGO
        LEFT JOIN grupo gr ON pr.GRUPO = gr.CODIGO
        LEFT JOIN impressora im ON gr.CODIGO_IMPRESSORA = im.CODIGO
        WHERE ci.fk_comanda_pessoa = ? AND (ci.impresso = 0 or ci.impresso is null)
    """, (codigo_pessoa,))
    
    grupos_sem_impressora = set()
    for codigo, descricao in aItens:
        if codigo is None:
            grupos_sem_impressora.add(descricao)

    if grupos_sem_impressora:
        msg = '\n'.join(grupos_sem_impressora)
        raise Exception(f'Grupo sem impressora configurada:\n{msg}')

    # Busca impressoras distintas
    aImpressoras = selectfb("""
        SELECT DISTINCT im.codigo
        FROM comanda_itens ci
        LEFT JOIN produto pr ON ci.FK_PRODUTO = pr.CODIGO
        LEFT JOIN grupo gr ON pr.GRUPO = gr.CODIGO
        LEFT JOIN impressora im ON gr.CODIGO_IMPRESSORA = im.CODIGO
        WHERE ci.fk_comanda_pessoa = ? AND (ci.impresso = 0 or ci.impresso is null)
    """, (codigo_pessoa,))
    
    codigos_impressoras = [linha[0] for linha in aImpressoras]

    for codigo_imp in codigos_impressoras:        
        nome_empresa = selectfb(f"SELECT FANTASIA FROM EMPRESA WHERE CODIGO = {empresa}")
        nome_empresa = nome_empresa[0]

        impressora = selectfb(f"SELECT COLUNAS, PORTA_IMPRESSORA, IMPRESSORA FROM IMPRESSORA WHERE CODIGO = {codigo_imp}")
        impressora = impressora[0]
        colunas = impressora[0]
        porta_impressora = impressora[1]
        impressora = impressora[2]

        aImpressao = []

        aImpressao.append(f"[b]-{nome_empresa[0]}[/b]")
        aImpressao.append("[ls]")
        aImpressao.append("[b][c]*** IMPRESSAO GRUPO ***[/c][/b]")
        aImpressao.append(f"MESA.....:{mesa}")
        aImpressao.append("[ld]")

        sCodigoTitulo = "|COD |"
        sQtdTitulo = "|   QTD|"
        iAntes = (sCodigoTitulo + 'PRODUTO').index('P')
        iDepois = len(sQtdTitulo)
        iQtdProduto = colunas - len(sCodigoTitulo) - iDepois
        sTitulo = sCodigoTitulo + 'PRODUTO'.ljust(iQtdProduto) + sQtdTitulo
        aImpressao.append(sTitulo)
        aImpressao.append("[ld]")

        # Itens da comanda para essa impressora
        aProduto = selectfb("""
            SELECT ci.FK_PRODUTO, pr.DESCRICAO, ci.QTD, ci.OBSERVACAO, ci.DATA_HORA
            FROM comanda_itens ci
            LEFT JOIN produto pr ON ci.FK_PRODUTO = pr.CODIGO
            LEFT JOIN grupo gr ON pr.GRUPO = gr.CODIGO
            LEFT JOIN impressora im ON gr.CODIGO_IMPRESSORA = im.CODIGO
            WHERE ci.fk_comanda_pessoa = ? AND im.codigo = ? AND (ci.impresso = 0 or ci.impresso is null)
        """, (codigo_pessoa, codigo_imp))

        for fk_produto, descricao, qtd, observacao, data_hora in aProduto:
            sProduto = f"|{str(fk_produto).ljust(len(sCodigoTitulo)-2)}|{descricao[:iQtdProduto].ljust(iQtdProduto)}|{format(qtd, '.2f').rjust(len(sQtdTitulo)-2)}|"
            aImpressao.append(sProduto)
            if observacao:
                for linha in quebra_linhas(observacao, colunas):
                    aImpressao.append(linha)
            aImpressao.append("[ls]")

        aImpressao.append("[ld]")
        if aProduto:
            aImpressao.append(f"Data: {aProduto[0][4]}")

        if impressora == 2:
            aImpressao.extend([' ' * colunas] * 5)

        # Salva em arquivo
        Path("Comanda.txt").write_text('\n'.join(aImpressao), encoding='utf-8')

        # Simulação de envio para impressora
        print(f"Imprimindo na porta {porta_impressora}:")
        print('\n'.join(aImpressao))
        time.sleep(3)

        if porta_impressora[:4] == 'RAW:':
            porta_impressora = porta_impressora[4:]

        impressao = '\n'.join(aImpressao)

        imprimir_texto_escpos(impressao, porta_impressora,colunas,impressora)

        # Marca como impresso
        # Itens da comanda para essa impressora
        aProduto = selectfb("""
            SELECT ci.codigo
            FROM comanda_itens ci
            LEFT JOIN produto pr ON ci.FK_PRODUTO = pr.CODIGO
            LEFT JOIN grupo gr ON pr.GRUPO = gr.CODIGO
            LEFT JOIN impressora im ON gr.CODIGO_IMPRESSORA = im.CODIGO
            WHERE ci.fk_comanda_pessoa = ? AND im.codigo = ? AND (ci.impresso = 0 or ci.impresso is null)
        """, (codigo_pessoa, codigo_imp))

        for codigo in aProduto:
            updatefb("""
                UPDATE comanda_itens
                SET impresso = 1
                WHERE codigo = ?
            """, codigo)


    updatefb("""
        UPDATE MESA
        SET impresso = 1
        WHERE codigo = ?
    """, (mesa,))      

def quebra_linhas(texto, largura):
    palavras = texto.split()
    linhas = []
    atual = ""
    for palavra in palavras:
        if len(atual) + len(palavra) + 1 <= largura:
            atual += (" " if atual else "") + palavra
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas    

def substituir_tags(texto: str, colunas: int) -> str:
    linha_simples = '-' * colunas
    linha_dupla = '=' * colunas

    texto = texto.replace('\n', '\r\n')
    texto = texto.replace('[b]', '\x1B\x45')
    texto = texto.replace('[/b]', '\x1B\x46')
    texto = texto.replace('[n]', '\x1B\x21\x00')
    texto = texto.replace('[g]', '\x1B\x21\x30')
    texto = texto.replace('[c]', '\x1B\x61\x01')
    texto = texto.replace('[/c]', '\x1B\x61\x00')
    texto = texto.replace('[e]', '\x1B\x61\x00')
    texto = texto.replace('[/e]', '\x1B\x61\x00')
    texto = texto.replace('[d]', '\x1B\x61\x02')
    texto = texto.replace('[/d]', '\x1B\x61\x00')
    texto = texto.replace('[ls]', linha_simples)
    texto = texto.replace('[ld]', linha_dupla)
    return texto

def imprimir_texto_escpos(texto: str, porta_impressora: str, colunas: int, tipo_impressora: int = 1):
    hPrinter = win32print.OpenPrinter(porta_impressora)
    try:
        texto = substituir_tags(texto, colunas)

        if tipo_impressora == 2:
            texto += ' \r\n' * 5

        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cupom ESC/POS", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, texto.encode('cp850'))  # ESC/POS geralmente usa cp850
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)

        time.sleep(0.15)

        # Corte
        hPrinter = win32print.OpenPrinter(porta_impressora)
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Corte", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        corte = '\n\n\n\n\n\n' + '\x1B\x69'
        win32print.WritePrinter(hPrinter, corte.encode('cp850'))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
    except Exception as e:
        raise Exception(f"Erro ao imprimir: {e}")    

def imprime_consumo_mesa(mesa, empresa):
    aMesas = selectfb(f"SELECT FK_MOVIMENTO FROM MESA WHERE CODIGO = {mesa}")
    aComanda = selectfb(f"SELECT CODIGO, TOTAL FROM COMANDA_PESSOA WHERE FK_COMANDA = {aMesas[0][0]}")

    codigo_pessoa = aComanda[0][0]
    total_geral = aComanda[0][1]

    if not aMesas:
        raise Exception("Mesa não encontrada")

    if not aComanda:
        raise Exception("Pessoa da comanda não encontrada")

    # Detalhes da comanda
    aProduto = selectfb(f"""
        SELECT ci.fk_produto, pr.descricao, ci.qtd, ci.preco, ci.total, ci.observacao
        FROM comanda_itens ci
        LEFT JOIN produto pr ON ci.fk_produto = pr.codigo
        WHERE ci.fk_comanda_pessoa = {codigo_pessoa} AND (ci.impresso = 0 or ci.impresso is null)
    """)

    empresa = selectfb(f"SELECT FANTASIA FROM EMPRESA WHERE CODIGO = {empresa}")
    empresa = empresa[0]

    nome_terminal = obter_nome_terminal()
    nome_terminal = nome_terminal.upper()    

    aImpressora = selectfb(f"""
        SELECT COLUNAS, PORTA_IMPRESSORA, IMPRESSORA, I.CODIGO 
        FROM IMPRESSORAS_PADROES IP
        LEFT JOIN IMPRESSORA I ON IP.CODIGO_IMPRESSORA = I.CODIGO
        WHERE MODULO = 'PDV' AND IP.NOME_TERMINAL = '{nome_terminal}'
    """)

    aImpressora = aImpressora[0]
    colunas = aImpressora[0]
    porta_impressora = aImpressora[1]
    impressora = aImpressora[2]    
    codigo_impressora = aImpressora[3]    
    
    aImpressao = []

    aImpressao.append(f"[e][b]-{empresa[0]}[/b][/e]")
    aImpressao.append("[ls]")
    aImpressao.append(f"[c][b]**** PEDIDO MESA No. {mesa} ***[/b][/c]")
    aImpressao.append("[ls]")

    titulo_base = "|COD |PRODUTO".ljust(colunas - 24) + "| QTD|"
    iAntes = titulo_base.find("PRODUTO")
    iDepois = len("| QTD|")
    iQtdProduto = colunas - len("|COD |") - iDepois
    sTitulo = "|COD |" + "PRODUTO".ljust(iQtdProduto) + "| QTD|"
    aImpressao.append(sTitulo)
    aImpressao.append("[ld]")

    if not len(aProduto) > 0:
        return

    for item in aProduto:
        cod = str(item[0]).ljust(4)
        desc = item[1][:iQtdProduto].ljust(iQtdProduto)
        qtd = f"{item[2]:.2f}".rjust(4)
        linha = f"|{cod}|{desc}|{qtd}|"
        aImpressao.append(linha)

        observacao = item[5]

        if observacao: 
            aImpressao.extend(quebra_linhas(observacao, colunas))

    if impressora == 2:
        aImpressao.extend([' ' * colunas] * 5)

    Path("caixa.txt").write_text("\n".join(aImpressao), encoding="utf-8")

    # Simulação de envio para impressora
    print_log(f"Imprimindo na porta {porta_impressora}", "servidor_socket")
    print_log('\n'.join(aImpressao), "servidor_socket")
    time.sleep(3)

    if porta_impressora[:4] == 'RAW:':
        porta_impressora = porta_impressora[4:]

    impressao = '\n'.join(aImpressao)    

    # Imprime
    imprimir_texto_escpos(impressao, porta_impressora, colunas, impressora)

    # Marca como impresso
    # Itens da comanda para essa impressora
    # aProduto = selectfb("""
    #     SELECT ci.codigo
    #     FROM comanda_itens ci
    #     LEFT JOIN produto pr ON ci.FK_PRODUTO = pr.CODIGO
    #     LEFT JOIN grupo gr ON pr.GRUPO = gr.CODIGO
    #     LEFT JOIN impressora im ON gr.CODIGO_IMPRESSORA = im.CODIGO
    #     WHERE ci.fk_comanda_pessoa = ? AND im.codigo = ? AND (ci.impresso = 0 or ci.impresso is null)
    # """, (codigo_pessoa, codigo_impressora))

    aProduto = selectfb("""select
                            ci.codigo
                        from
                            comanda_itens ci
                        left join
                            produto pr
                            on ci.fk_produto = pr.codigo
                        where ci.fk_comanda_pessoa = ?""", (codigo_pessoa,))

    for codigo in aProduto:
        updatefb("""
            UPDATE comanda_itens
            SET impresso = 1
            WHERE codigo = ?
        """, (codigo))    

    updatefb(f"""
        UPDATE MESA
        SET impresso = 1
        WHERE codigo = ?
    """, (mesa,))              

def imprime_pedido_mesa(mesa, empresa):
    aMesas = selectfb(f"SELECT FK_MOVIMENTO FROM MESA WHERE CODIGO = {mesa}")
    aComanda = selectfb(f"SELECT CODIGO, TOTAL FROM COMANDA_PESSOA WHERE FK_COMANDA = {aMesas[0][0]}")

    codigo_pessoa = aComanda[0][0]
    total_geral = aComanda[0][1]

    if not aMesas:
        raise Exception("Mesa não encontrada")

    if not aComanda:
        raise Exception("Pessoa da comanda não encontrada")

    # Detalhes da comanda
    aProduto = selectfb(f"""
        SELECT ci.fk_produto, pr.descricao, ci.qtd, ci.preco, ci.total, ci.observacao
        FROM comanda_itens ci
        LEFT JOIN produto pr ON ci.fk_produto = pr.codigo
        WHERE ci.fk_comanda_pessoa = {codigo_pessoa} 
    """)

    empresa = selectfb(f"SELECT FANTASIA FROM EMPRESA WHERE CODIGO = {empresa}")
    empresa = empresa[0]

    nome_terminal = obter_nome_terminal()
    nome_terminal = nome_terminal.upper()    

    impressora = selectfb(f"""
        SELECT COLUNAS, PORTA_IMPRESSORA, IMPRESSORA 
        FROM IMPRESSORAS_PADROES IP
        LEFT JOIN IMPRESSORA I ON IP.CODIGO_IMPRESSORA = I.CODIGO
        WHERE MODULO = 'PDV' AND IP.NOME_TERMINAL = '{nome_terminal}'
    """)

    impressora = impressora[0]
    colunas = impressora[0]
    porta_impressora = impressora[1]
    impressora = impressora[2]    

    aImpressao = []

    aImpressao.append(f"[e][b]-{empresa[0]}[/b][/e]")
    aImpressao.append("[ls]")
    aImpressao.append(f"[c][b]**** PEDIDO MESA No. {mesa} ***[/b][/c]")
    aImpressao.append("[ls]")

    titulo_base = "|COD |PRODUTO".ljust(colunas - 24) + "| QTD|  VALOR|  TOTAL|"
    iAntes = titulo_base.find("PRODUTO")
    iDepois = len("| QTD|  VALOR|  TOTAL|")
    iQtdProduto = colunas - len("|COD |") - iDepois
    sTitulo = "|COD |" + "PRODUTO".ljust(iQtdProduto) + "| QTD|  VALOR|  TOTAL|"
    aImpressao.append(sTitulo)
    aImpressao.append("[ld]")

    for item in aProduto:
        cod = str(item[0]).ljust(4)
        desc = item[1][:iQtdProduto].ljust(iQtdProduto)
        qtd = f"{item[2]:.2f}".rjust(4)
        preco = f"{item[3]:.2f}".rjust(7)
        total = f"{item[4]:.2f}".rjust(7)
        linha = f"|{cod}|{desc}|{qtd}|{preco}|{total}|"
        aImpressao.append(linha)

        observacao = item[5]

        if observacao:
            if isinstance(observacao, bytes):
                observacao = observacao.decode('utf-8')
            aImpressao.extend(quebra_linhas(observacao, colunas))

    aImpressao.append("[ls]")
    aImpressao.append(f"[e]TOTAL     :{total_geral}[/e]")
    aImpressao.append("[ls]")
    aImpressao.append("NAO E DOCUMENTO FISCAL")
    aImpressao.extend(quebra_linhas("<<" + "Volte Sempre"[:colunas] + ">>", colunas))

    if impressora == 2:
        aImpressao.extend([' ' * colunas] * 5)

    Path("caixa.txt").write_text("\n".join(aImpressao), encoding="utf-8")

    # Simulação de envio para impressora
    print_log(f"Imprimindo na porta {porta_impressora}", "servidor_socket")
    print_log('\n'.join(aImpressao), "servidor_socket")
    time.sleep(3)

    if porta_impressora[:4] == 'RAW:':
        porta_impressora = porta_impressora[4:]

    impressao = '\n'.join(aImpressao)    

    # Imprime
    imprimir_texto_escpos(impressao, porta_impressora, colunas, impressora)

def verifica_impressora():
    ip_servidor = get_local_ip()
    try:
        cursor = parametros.FIREBIRD_CONNECTION.cursor()
        cursor.execute(f"select vt.porta from vendas_terminais vt where vt.ip = '{ip_servidor}' and vt.tipoimpressora = 2")
        result = cursor.fetchall()
        impressora = result[0][0]
        printer_name = f'\\\\{ip_servidor}\\{impressora[4:]}'
        return printer_name
    except Exception as e:
        erro_msg = f'Erro ao adquirir impressora: {e}'
        print_log(erro_msg, "servidor_socket")

def imprime_documento(texto, porta_impressora = None):
    import win32print

    # Configurações da impressora
    # printer_name = '\\\\192.168.10.93\\MP-4200 TH'
    if porta_impressora != None:
        printer_name = porta_impressora
    else:
        printer_name = configurar_pos_printer('PDV')

    print_log(f'Imprimindo na impressora {printer_name}', "servidor_socket")



    # Comando de corte (dependendo da impressora, isso pode variar)
    # Comando ESC/POS para corte total: '\x1d\x56\x00'
    # Comando ESC/POS para corte parcial: '\x1d\x56\x01'
    corte = '\x1d\x56\x00'

    printer_name = printer_name.replace("RAW:", "")

    # Conectar e iniciar o trabalho de impressão
    printer_handle = win32print.OpenPrinter(printer_name)
    job = win32print.StartDocPrinter(printer_handle, 1, ("Impressão Python", None, "RAW"))
    win32print.StartPagePrinter(printer_handle)

    # Comando para aumentar fonte (2x altura e largura)
    # aumentar_fonte = b'\x1B\x21\x30'
    fonte_normal = b'\x1B\x21\x00'
    # Enviar o comando para aumentar fonte
    win32print.WritePrinter(printer_handle, fonte_normal)

    

    # Enviar o texto para a impressora
    win32print.WritePrinter(printer_handle, texto.encode('cp850', errors='replace'))

    # Enviar o comando de corte para a impressora
    win32print.WritePrinter(printer_handle, corte.encode('utf-8'))

    # Finalizar a impressão
    win32print.EndPagePrinter(printer_handle)
    win32print.EndDocPrinter(printer_handle)
    win32print.ClosePrinter(printer_handle)

servidor_socket()