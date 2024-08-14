from funcoes import *
import fdb
import zlib
import parametros

def xmlcontador():
    print_log("Carrega configurações- xmlcontador")
    carregar_configuracoes()
    try:
        print_log("Pega dados local - xmlcontador")
        cnpjs_verificados = []
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            pasta_compartilhada_backup = dados_cnpj['pasta_compartilhada_backup']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
            caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
            porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
            caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil']
            caminho_gbak_firebird_gfil = dados_cnpj['caminho_gbak_firebird_gfil']
            porta_firebird_gfil = dados_cnpj['porta_firebird_gfil']

            if cnpj in cnpjs_verificados:
                continue

            if ativo:
                conMYSQL = parametros.MYSQL_CONNECTION
                con = parametros.FIREBIRD_CONNECTION
                dias_busca_nota = -15
                
                print_log("Inicia select das notas - xmlcontador")
                if sistema_em_uso == '1':  # maxsuport
                    if pasta_compartilhada_backup and caminho_base_dados_maxsuport and caminho_gbak_firebird_maxsuport and porta_firebird_maxsuport:

                        cur = con.cursor()  # Aqui é a conexão do maxsuport
                        
                        # Loop sobre os cnpjs e inscrições do banco de dados
                        cur.execute('select codigo, cnpj, ie from empresa')
                        cnpjs_ies = cur.fetchall()
                        for cnpj_ie in cnpjs_ies:
                            codigo_empresa = cnpj_ie[0]
                            cnpj = cnpj_ie[1]
                            cliente_ie = cnpj_ie[2]
                            cnpjs_verificados.append(cnpj)

                            cur.execute(f'''select c.nome,c.cnpj,c.cpf, e.cnpj as cnpjempresa, e.codigo 
                                        from empresa e 
                                        left outer join contador c 
                                            on c.fk_empresa = e.codigo
                                        where e.cnpj = '{cnpj}' AND e.codigo = {codigo_empresa}''')
                            rows = cur.fetchall()
                            rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                            curPlataform = conMYSQL.cursor()  # Conexão com o banco da plataforma
                            for row in rows_dict:
                                condicao = row['CPF'] if row['CPF'] else row['CNPJ']
                                contador = 0
                               # codigo_empresa = row['CODIGO']
                                
                                curPlataform.execute(f'select * from notafiscal_contador where cpf_cnpj = "{condicao}" ')
                                rowsPlat = curPlataform.fetchall()
                                rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]

                                cnpj_empresa = row['CNPJEMPRESA']

                                # Salva contador
                                # print_log("Inicia select contador - xmlcontador")
                                # if not rowsPlat:
                                #     nome = row['NOME']
                                #     cpf_cnpj = condicao
                                #     curPlataform.execute(f'insert into notafiscal_contador(nome,cpf_cnpj,cnpj_empresa) values("{nome}","{cpf_cnpj}","{cnpj_empresa}")')

                                # curPlataform.execute(f'select * from notafiscal_contador where cpf_cnpj = "{condicao}"')
                                # rowsPlat = curPlataform.fetchall()
                                # rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]
                                
                                contador = rows_dict_plat[0]['id']  # get id contador

                                # Vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É MDFE
                                print_log("Inicia select MDFE - xmlcontador")
                                cur.execute(f"select n.numero_mdfe,n.chave,n.data_emissao,n.serie,n.fk_empresa, n.xml, n.situacao from mdfe_master n where situacao in ('T','C') and data_emissao > dateadd(day, {dias_busca_nota}, current_date) and n.fk_empresa = ?", (codigo_empresa,))
                                rowsNotas = cur.fetchall()
                                rows_dict_notas = [dict(zip([column[0] for column in cur.description], rowNota)) for rowNota in rowsNotas]
                                for row_nota in rows_dict_notas:
                                    numero = row_nota['NUMERO_MDFE']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'MDFE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DATA_EMISSAO']
                                    xml = row_nota['XML']
                                    xml_cancelamento = ''
                                    cliente_id = cnpj_empresa
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                                # Vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É NFE
                                print_log("Inicia select NFE - xmlcontador")
                                cur.execute(f'select numero, chave, data_emissao, serie, fkempresa, xml, xml_cancelamento, situacao from nfe_master where situacao in (2,3,5) and data_emissao > dateadd(day, {dias_busca_nota}, current_date) and fkempresa = ?', (codigo_empresa,))
                                rowsNotas = cur.fetchall()
                                rows_dict_notas = [dict(zip([column[0] for column in cur.description], rowNota)) for rowNota in rowsNotas]
                                for row_nota in rows_dict_notas:
                                    numero = row_nota['NUMERO']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'NFE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DATA_EMISSAO']
                                    xml = row_nota['XML']
                                    xml_cancelamento = row_nota['XML_CANCELAMENTO']
                                    cliente_id = cnpj_empresa
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)
                                    
                                # Vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É NFCE
                                print_log("Inicia select NFCE - xmlcontador")
                                cur.execute(f"select numero, chave, data_emissao, serie, fkempresa, xml, xml_cancelamento, situacao from nfce_master where situacao in ('T','C','I') and chave <> 'CHAVE NÃO GERADA' and data_emissao > dateadd(day, {dias_busca_nota}, current_date) and fkempresa = ?", (codigo_empresa,))
                                rowsNotas = cur.fetchall()
                                rows_dict_notas = [dict(zip([column[0] for column in cur.description], rowNota)) for rowNota in rowsNotas]
                                for row_nota in rows_dict_notas:
                                    numero = row_nota['NUMERO']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'NFCE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DATA_EMISSAO']
                                    xml = row_nota['XML']
                                    xml_cancelamento = row_nota['XML_CANCELAMENTO']
                                    cliente_id = cnpj_empresa
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                                # Vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É COMPRAS
                                print_log("Inicia select COMPRAS - xmlcontador")
                                cur.execute(f"select nr_nota, chave, dtentrada, serie, empresa, xml from compra where chave is not null and dtentrada > dateadd(day, {dias_busca_nota}, current_date) and empresa = ?", (codigo_empresa,))
                                rowsNotas = cur.fetchall()
                                rows_dict_notas = [dict(zip([column[0] for column in cur.description], rowNota)) for rowNota in rowsNotas]
                                for row_nota in rows_dict_notas:
                                    numero = row_nota['NR_NOTA']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'COMP'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DTENTRADA']
                                    xml = row_nota['XML']
                                    xml_cancelamento = ''
                                    cliente_id = cnpj_empresa
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                            conMYSQL.commit()
                                
                elif sistema_em_uso == '2':  # gfil
                    if pasta_compartilhada_backup and caminho_base_dados_gfil and caminho_gbak_firebird_gfil:
                        con = fdb.connect(
                            host='localhost',
                            database=caminho_base_dados_gfil,
                            user='GFILMASTER',
                            password='b32@m451',
                            port=int(porta_firebird_gfil)
                        )

                        cur = con.cursor()

                        cur.execute("select d.filial ,case when (d.cnpj = '' or (d.cnpj is null) ) then d.cpf else d.cnpj end as cnpj, d.ie from diversos d")
                        cnpjs_ies = cur.fetchall()
                        for cnpj_ie in cnpjs_ies:
                            codigo_empresa = cnpj_ie[0]
                            cnpj = cnpj_ie[1]
                            cliente_ie = cnpj_ie[2]
                            cnpjs_verificados.append(cnpj)

                            # Dados do contador
                            cur.execute(f'''SELECT c.NOME, c.CPF, c.CNPJ, d.CNPJ as cnpj_empresa, d.FILIAL  
                                        FROM CONTABILISTA c 
                                            LEFT OUTER JOIN DIVERSOS d 
                                            ON c.FILIAL = d.FILIAL 
                                        WHERE d.CNPJ = '{cnpj}' OR (d.CPF = '{cnpj}') AND d.FILIAL = '{codigo_empresa}' ''')
                            rows = cur.fetchall()
                            rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                            curPlataform = conMYSQL.cursor()  # Conexão com o banco da plataforma
                            for row in rows_dict:
                                condicao = row['CPF'] if row['CPF'] else row['CNPJ']
                               # codigo_empresa = row['FILIAL']

                                contador = 0
                                
                                curPlataform.execute(f'select * from notafiscal_contador where cpf_cnpj = "{condicao}"')
                                rowsPlat = curPlataform.fetchall()
                                rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]                            

                                # Salva contador
                                print_log("Inicia select contador - xmlcontador")
                                if not rowsPlat:
                                    nome = row['NOME']
                                    cpf_cnpj = condicao
                                    cnpj_empresa = row['CNPJ_EMPRESA']
                                    curPlataform.execute(f'insert into notafiscal_contador(nome, cpf_cnpj, cnpj_empresa) values("{nome}", "{cpf_cnpj}", "{cnpj_empresa}")')

                                curPlataform.execute(f'select * from notafiscal_contador where cpf_cnpj = "{condicao}"')
                                rowsPlat = curPlataform.fetchall()
                                rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]
                                
                                contador = rows_dict_plat[0]['id']  # get id contador

                                # Salva notas NFE
                                cur.execute(f'''SELECT c.NOME, c.CPF, c.CNPJ, d.CNPJ as CNPJ_EMPRESA, DATA_EMIS_NFE, XML, XML_CANCELAM, n.NUMERO, n.CHAVE, n.SERIE  
                                            FROM CONTABILISTA c 
                                                LEFT OUTER JOIN DIVERSOS d 
                                                ON c.FILIAL = d.FILIAL 
                                                LEFT OUTER JOIN NFE_MESTRE n 
                                                ON n.FILIAL = d.FILIAL 
                                            WHERE n.DATA_EMIS_NFE > dateadd(day, {dias_busca_nota}, current_date) AND d.FILIAL={codigo_empresa}''')
                                
                                rows = cur.fetchall()
                                rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                for row_nota in rows_dict:
                                    try:
                                        xml = zlib.decompress(row_nota['XML']).decode('utf-8')
                                    except:
                                        print_log('Nota não existe')
                                        xml = ''
                                    try:
                                        xml_cancelamento = zlib.decompress(row_nota['XML_CANCELAM']).decode('utf-8')
                                    except:
                                        xml_cancelamento = ''
                                        print_log('Nota cancelamento não existe')

                                    numero = row_nota['NUMERO']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'NFE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DATA_EMIS_NFE']
                                    cliente_id = row_nota['CNPJ_EMPRESA']
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                                # Salva notas NFCE
                                cur.execute(f'''SELECT c.NOME, c.CPF, c.CNPJ, d.CNPJ as CNPJ_EMPRESA, DHEMI, XML, XML_CANCELAM, n.NUMERO, n.CHAVE, n.SERIE  
                                            FROM CONTABILISTA c 
                                                LEFT OUTER JOIN DIVERSOS d 
                                                ON c.FILIAL = d.FILIAL 
                                                LEFT OUTER JOIN NFCE_MESTRE n 
                                                ON n.FILIAL = d.FILIAL 
                                            WHERE n.DHEMI > dateadd(day, {dias_busca_nota}, current_date) AND d.FILIAL={codigo_empresa}''')
                                
                                rows = cur.fetchall()
                                rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                for row_nota in rows_dict:
                                    try:
                                        xml = zlib.decompress(row_nota['XML']).decode('utf-8')
                                    except:
                                        print_log('Nota não existe')
                                        xml = ''
                                    try:
                                        xml_cancelamento = zlib.decompress(row_nota['XML_CANCELAM']).decode('utf-8')
                                    except:
                                        xml_cancelamento = ''
                                        print_log('Nota de cancelamento não existe')

                                    numero = row_nota['NUMERO']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'NFCE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DHEMI']
                                    cliente_id = row_nota['CNPJ_EMPRESA']
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                                # Salva notas CTE
                                cur.execute(f'''SELECT c.NOME, c.CPF, c.CNPJ, d.CNPJ as CNPJ_EMPRESA, DHEMI, XML, XML_CANCELAM, n.NUMERO, n.CHAVE, n.SERIE  
                                            FROM CONTABILISTA c 
                                                LEFT OUTER JOIN DIVERSOS d 
                                                ON c.FILIAL = d.FILIAL 
                                                LEFT OUTER JOIN CTE_MESTRE n 
                                                ON n.FILIAL = d.FILIAL 
                                            WHERE n.DHEMI > dateadd(day, {dias_busca_nota}, current_date) AND d.FILIAL={codigo_empresa}''')
                                
                                rows = cur.fetchall()
                                rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                for row_nota in rows_dict:
                                    try:
                                        xml = zlib.decompress(row_nota['XML']).decode('utf-8')
                                    except:
                                        print_log('Nota não existe')
                                        xml = ''
                                    try:
                                        xml_cancelamento = zlib.decompress(row_nota['XML_CANCELAM']).decode('utf-8')
                                    except:
                                        xml_cancelamento = ''
                                        print_log('Nota de cancelamento não existe')

                                    numero = row_nota['NUMERO']
                                    chave = row_nota['CHAVE']
                                    tipo_nota = 'CTE'
                                    serie = row_nota['SERIE']
                                    data_nota = row_nota['DHEMI']
                                    cliente_id = row_nota['CNPJ_EMPRESA']
                                    contador_id = contador

                                    SalvaNota(conMYSQL, numero, chave, tipo_nota, serie, data_nota, xml, xml_cancelamento, cliente_id, contador_id, cliente_ie)

                        conMYSQL.commit()

    except Exception as e:
        if conMYSQL:
            conMYSQL.rollback()
        print_log(f"Erro: {e}")


xmlcontador()