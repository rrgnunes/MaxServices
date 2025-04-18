from funcoes import print_log,carregar_configuracoes,exibe_alerta, configurar_pos_printer,inicializa_conexao_firebird, selectfb
import socket
import threading
import json
import fdb
from datetime import datetime, date
from decimal import Decimal
import parametros
import base64

lImprimeGrupo = False

def get_local_ip():
    """
    Obtém o endereço IP local da máquina.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não precisa realmente enviar dados para obter o IP
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

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
                            efetua_impressao_por_grupo(sMesa, sEmpresa)
                        else:
                            efetua_impressao_comanda(sMesa, sEmpresa)
                    elif sTipoImpressao == 'ResumoMesa':
                        efetua_impressao_resumo_mesa(sMesa, sEmpresa)
                    send_response(conn, '200')
                elif sTipo == '5':
                    comando_sql = request[1:].split(';')[0]
                    resultado = consulta_completa(comando_sql)
                    send_response(conn, resultado)
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


def send_response(conn, response):
    response += '\n'
    response_bytes = response.encode('utf-8')
    conn.sendall(response_bytes)

def mostrar_alerta(mensagem):
    exibe_alerta(mensagem)

def efetua_impressao_por_grupo(mesa, empresa):
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird()
        cursor = parametros.FIREBIRD_CONNECTION.cursor()

        cursor.execute(f"""
            SELECT ci.codigo AS codigounico, ci.qtd, ci.observacao, ci.preco, ci.total,
                   pr.codigo AS codigoproduto, pr.descricao, gr.descricao AS grupo_nome,
                   im.codigo AS codigo_impressora, im.PORTA_IMPRESSORA AS nome_impressora,
                   me.nome AS mesa_nome, em.fantasia, cm.data_hora
            FROM comanda_itens ci
            LEFT JOIN produto pr ON ci.fk_produto = pr.codigo
            LEFT JOIN grupo gr ON pr.grupo = gr.codigo
            LEFT JOIN impressora im ON gr.codigo_impressora = im.codigo
            LEFT JOIN comanda_pessoa cp ON ci.fk_comanda_pessoa = cp.codigo
            LEFT JOIN comanda_master cm ON cp.fk_comanda = cm.codigo
            LEFT JOIN mesa me ON cm.codigo = me.fk_movimento
            LEFT JOIN empresa em ON pr.empresa = em.codigo
            WHERE coalesce(ci.impresso,0) = 0 and me.codigo = {mesa} AND ci.situacao = 'S' and em.codigo = {empresa}
        """)

        rows = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        itens = [dict(zip(colunas, row)) for row in rows]

        # Verifica se há grupo sem impressora
        grupos_sem_impressora = set()
        for item in itens:
            if item['CODIGO_IMPRESSORA'] is None:
                grupos_sem_impressora.add(item['GRUPO_NOME'])

        if grupos_sem_impressora:
            msg = "Grupos sem impressora configurada:\n" + "\n".join(grupos_sem_impressora)
            print_log(msg, "servidor_socket")
            return

        # Agrupa os itens por impressora
        impressoras = {}
        for item in itens:
            cod_imp = item['CODIGO_IMPRESSORA']
            if cod_imp not in impressoras:
                impressoras[cod_imp] = []
            impressoras[cod_imp].append(item)

        # Imprime para cada impressora
        for cod_imp, lista_itens in impressoras.items():
            imprimir_comanda_formatada(lista_itens)

    except Exception as e:
        erro_msg = f"Erro ao processar impressão: {e}"
        print_log(erro_msg, "servidor_socket")


def imprimir_comanda_formatada(itens):
    if not itens:
        return

    empresa = itens[0]['FANTASIA']
    mesa = itens[0]['MESA_NOME']
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    porta_impressora = itens[0]['NOME_IMPRESSORA']

    def ajustar_descricao(descricao):
        descricao = descricao[:40]
        partes = [descricao[i:i+20] for i in range(0, len(descricao), 20)]
        if len(partes) == 1:
            partes.append('')
        return partes

    negrito_on = '\x1b\x45\x01'
    negrito_off = '\x1b\x45\x00'

    texto = f"{empresa}\n\n"
    texto += "       *** PEDIDO DA MESA ***\n\n"
    texto += f"Mesa: {mesa}\n\n"
    texto += "COD  | PRODUTO              | QTD \n"
    texto += "----------------------------------\n"

    for item in itens:
        desc = ajustar_descricao(item['DESCRICAO'])
        texto += f"{item['CODIGOPRODUTO']: <4} - {desc[0]: <20}   {item['QTD']}\n"
        texto += f"       {desc[1]: <20}\n"
        if item['OBSERVACAO']:
            texto += f"{negrito_on}OBS: {item['OBSERVACAO'].decode('utf-8')}{negrito_off}\n"
        texto += "----------------------------------\n"

    texto += f"Data: {data_atual}\n"
    texto += "----------------------------------\n"
    texto += "----------------------------------\n"
    texto += "----------------------------------\n"
    texto += "----------------------------------\n"
    texto += "----------------------------------\n"

    imprime_documento(texto, porta_impressora)

    # Atualiza os itens como impressos
    try:
        cursor = parametros.FIREBIRD_CONNECTION.cursor()
        for item in itens:
            cursor.execute(f"UPDATE comanda_itens SET impresso = 1 WHERE codigo = {item['CODIGOUNICO']}")
        parametros.FIREBIRD_CONNECTION.commit()
    except Exception as e:
        print_log(f"Erro ao atualizar situação: {e}", "servidor_socket")

def efetua_impressao_comanda(mesa, empresa):
    impressao = ''
    try:
        if parametros.FIREBIRD_CONNECTION.closed:
            inicializa_conexao_firebird();        
        cursor = parametros.FIREBIRD_CONNECTION.cursor()

        cursor.execute(f"""select ci.codigo as codigounico, cm.codigo, cm.data_hora, me.nome, PR.CODIGO as codigoproduto, pr.descricao, ci.qtd,ci.observacao,ci.PRECO ,ci.TOTAL, em.FANTASIA  
                           from mesa me
                           left outer join comanda_master cm
                           on me.fk_movimento = cm.codigo
                           left outer join comanda_pessoa cp
                           on cm.codigo = cp.fk_comanda
                           left outer join comanda_itens ci
                           on cp.codigo= ci.fk_comanda_pessoa
                           left outer join produto pr
                           on ci.fk_produto = pr.codigo
                           LEFT OUTER JOIN EMPRESA em 
                             ON pr.EMPRESA = em.CODIGO 
                           where me.codigo={mesa} AND ci.SITUACAO = 'S'
                       """)
        rows = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        # Criar uma lista de dicionários
        resultado = [dict(zip(colunas, row)) for row in rows]
        # Calcular o total
        total = sum(float(item['TOTAL']) for item in resultado)

        # Obter a data atual
        data_atual = datetime.now().strftime('%d/%m/%Y')

        # Função para ajustar a descrição
        def ajustar_descricao(descricao):
            descricao = descricao[:40]  # Limitar a string a 40 caracteres (2 linhas de 20)
            partes = [descricao[i:i+20] for i in range(0, len(descricao), 20)]
            if len(partes) == 1:
                partes.append('')
            return partes
        
        # Códigos ESC/POS para negrito
        negrito_on = '\x1b\x45\x01'
        negrito_off = '\x1b\x45\x00'        

        # Gerar a string para impressão
        impressao = f"{resultado[0]['FANTASIA']}\n\n"        
        impressao += "       *** PEDIDO DA MESA ***\n\n"
        impressao += f"Mesa: {resultado[0]['NOME']}\n\n"
        impressao += "COD  | PRODUTO              | QTD \n"

        for item in resultado:
            descricao_ajustada = ajustar_descricao(item['DESCRICAO'])
            impressao += f"{item['CODIGOPRODUTO']: <4} - {descricao_ajustada[0]: <20}   {item['QTD']}\n"
            impressao += f"       {descricao_ajustada[1]: <20}       \n"
            impressao += f"{negrito_on}{item['OBSERVACAO'].decode('utf-8')}{negrito_off}\n"            
            impressao += "------------------------------------------\n"  # Linha de separação

        impressao += f"Data: {data_atual}     \n"

        # imprime a string gerada
        imprime_documento(impressao)

        # Marca como impresso
        for item in resultado:
            cursor = parametros.FIREBIRD_CONNECTION.cursor()
            sql = f"UPDATE comanda_itens SET impresso=1 WHERE CODIGO={item['CODIGOUNICO']}"
            cursor.execute(sql)
            parametros.FIREBIRD_CONNECTION.commit()

        print(f"Impressão comanda: Mesa {mesa}, Empresa {empresa}")
    except fdb.fbcore.DatabaseError as e:
        erro_msg = f"Erro no Banco de Dados: {e}"
        print_log(erro_msg, "servidor_socket")
        return json.dumps({'erro': erro_msg})
    except Exception as e:
        erro_msg = f"Erro ao executar comando SQL: {e}"
        print_log(erro_msg, "servidor_socket")
        return json.dumps({'erro': erro_msg})  

def efetua_impressao_resumo_mesa(mesa, empresa):
    impressao = ''
    try:
           
        cursor = parametros.FIREBIRD_CONNECTION.cursor()

        cursor.execute(f"""select cm.codigo, cm.data_hora, me.nome, PR.CODIGO as codigoproduto, pr.descricao, ci.qtd,ci.observacao,ci.PRECO ,ci.TOTAL, em.FANTASIA  
                           from mesa me
                           left outer join comanda_master cm
                           on me.fk_movimento = cm.codigo
                           left outer join comanda_pessoa cp
                           on cm.codigo = cp.fk_comanda
                           left outer join comanda_itens ci
                           on cp.codigo= ci.fk_comanda_pessoa
                           left outer join produto pr
                           on ci.fk_produto = pr.codigo
                           LEFT OUTER JOIN EMPRESA em 
                             ON pr.EMPRESA = em.CODIGO 
                           where me.codigo={mesa}
                       """)
        rows = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        # Criar uma lista de dicionários
        resultado = [dict(zip(colunas, row)) for row in rows]
        # Calcular o total
        total = sum(float(item['TOTAL']) for item in resultado)

        # Obter a data atual
        data_atual = datetime.now().strftime('%d/%m/%Y')

        # Função para ajustar a descrição
        def ajustar_descricao(descricao):
            descricao = descricao[:40]  # Limitar a string a 40 caracteres (2 linhas de 20)
            partes = [descricao[i:i+20] for i in range(0, len(descricao), 20)]
            if len(partes) == 1:
                partes.append('')
            return partes

        # Gerar a string para impressão
        impressao = f"{resultado[0]['FANTASIA']}\n\n"        
        impressao += "       *** RESUMO DA MESA ***\n\n"
        impressao += f"Mesa: {resultado[0]['NOME']}\n\n"
        impressao += "COD  | PRODUTO              | QTD x PRECO\n"
        impressao += "                                    TOTAL\n"

        for item in resultado:
            descricao_ajustada = ajustar_descricao(item['DESCRICAO'])
            impressao += f"{item['CODIGOPRODUTO']: <4} - {descricao_ajustada[0]: <20}   {item['QTD']} x {item['PRECO']:.2f}\n"
            impressao += f"       {descricao_ajustada[1]: <20}       {item['TOTAL']:.2f}\n"
            impressao += "------------------------------------------\n"  # Linha de separação

        impressao += f"Data: {data_atual}     Total: R$ {total:.2f}\n"


        # imprime a string gerada
        imprime_documento(impressao)
        print(f"Impressão Resumo Mesa: Mesa {mesa}, Empresa {empresa}")
    except fdb.fbcore.DatabaseError as e:
        erro_msg = f"Erro no Banco de Dados: {e}"
        print_log(erro_msg, "servidor_socket")
        return json.dumps({'erro': erro_msg})
    except Exception as e:
        erro_msg = f"Erro ao executar comando SQL: {e}"
        print_log(erro_msg, "servidor_socket")
        return json.dumps({'erro': erro_msg})  

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

    # Adicionar linhas em branco antes do comando de corte
    linhas_em_branco = "\n\n\n\n\n\n"

    # Comando de corte (dependendo da impressora, isso pode variar)
    # Comando ESC/POS para corte total: '\x1d\x56\x00'
    # Comando ESC/POS para corte parcial: '\x1d\x56\x01'
    corte = '\x1d\x56\x00'

    printer_name = printer_name.replace("RAW:", "")

    # Conectar e iniciar o trabalho de impressão
    printer_handle = win32print.OpenPrinter(printer_name)
    job = win32print.StartDocPrinter(printer_handle, 1, ("Impressão Python", None, "RAW"))
    win32print.StartPagePrinter(printer_handle)

    # Enviar o texto para a impressora
    win32print.WritePrinter(printer_handle, texto.encode('cp850', errors='replace'))
    win32print.WritePrinter(printer_handle, linhas_em_branco.encode('utf-8'))

    # Enviar o comando de corte para a impressora
    win32print.WritePrinter(printer_handle, corte.encode('utf-8'))

    # Finalizar a impressão
    win32print.EndPagePrinter(printer_handle)
    win32print.EndDocPrinter(printer_handle)
    win32print.ClosePrinter(printer_handle)

servidor_socket()