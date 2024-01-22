from funcoes import *

class threadxmlcontador(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.xmlcontador()             

    def xmlcontador(self):
        print_log(f"Carrega configurações da thread - xmlcontador")
        intervalo = -1
        while intervalo == -1:
            path_config_thread = SCRIPT_PATH + "/config.json"
            if os.path.exists(path_config_thread):
                with open(path_config_thread, 'r') as config_file:
                    config_thread = json.load(config_file)
            intervalo = config_thread['time_thread_xmlcontador']
        while not self.event.wait(intervalo):
            # Conexão com o banco de dados
            try:
                print_log(f"pega dados local - xmlcontador")
                if os.path.exists("C:/Users/Public/config.json"):
                    with open('C:/Users/Public/config.json', 'r') as config_file:
                        config = json.load(config_file)
                    for cnpj in config['sistema']:
                        parametros = config['sistema'][cnpj]
                        ativo = parametros['sistema_ativo'] == '1'
                        sistema_em_uso = parametros['sistema_em_uso_id']
                        pasta_compartilhada_backup = parametros['pasta_compartilhada_backup']
                        caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                        caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                        porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                        caminho_base_dados_gfil = parametros['caminho_base_dados_gfil']
                        caminho_gbak_firebird_gfil = parametros['caminho_gbak_firebird_gfil']
                        porta_firebird_gfil = parametros['porta_firebird_gfil']
                        data_hora = datetime.datetime.now()
                        data_hora_formatada = data_hora.strftime(
                            '%Y_%m_%d_%H_%M_%S')
                        timer_minutos_backup = parametros['timer_minutos_backup']

                        if ativo:
                            conMYSQL = mysql.connector.connect(
                                host=HOSTMYSQL,
                                user=USERMYSQL,
                                password=PASSMYSQL,
                                database=BASEMYSQL
                            )

                            dias_busca_nota = -50
                          
                            print_log(f"Inicia select das notas - xmlcontador")
                            if sistema_em_uso == '1':  # maxsuport
                                if pasta_compartilhada_backup != '' and \
                                        caminho_base_dados_maxsuport != '' and \
                                        caminho_gbak_firebird_maxsuport != '' and \
                                        porta_firebird_maxsuport != '':
                                    ofdb = fdb.load_api(
                                        f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll')
                                    con = fdb.connect(
                                        host='localhost',
                                        database=caminho_base_dados_maxsuport,
                                        user='sysdba',
                                        password='masterkey',
                                        port=int(porta_firebird_maxsuport)
                                    )

                                    cur = con.cursor() # Aqui é a conexão do maxsuport
                                    cur.execute(f'''select c.nome,c.cnpj,c.cpf, e.cnpj as cnpjempresa, e.codigo 
                                                from empresa e 
                                                left outer join contador c 
                                                    on c.fk_empresa = e.codigo
                                                where e.cnpj = '{cnpj}' ''')
                                    rows = cur.fetchall()
                                    rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                    curPlataform = conMYSQL.cursor()  # Aqui eu crio a conexão do banco da plataforma, se liga papito
                                    for row in rows_dict:
                                        condicao = row['CPF']
                                        if condicao is None:
                                            condicao = row['CNPJ']

                                        contador = 0
                                        codigo_empresa = row['CODIGO']
                                        
                                        curPlataform.execute(f'select * from notafiscal_contador nc where cpf_cnpj = "{condicao}" ')
                                        rowsPlat=curPlataform.fetchall()
                                        rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]

                                        cnpj_empresa = row['CNPJEMPRESA'] 

                                        #salvo contador
                                        print_log(f"Inicia select contador - xmlcontador")
                                        if len(rowsPlat) == 0:
                                            nome = row['NOME']
                                            cpf_cnpj = condicao
                                            curPlataform.execute(f'insert into notafiscal_contador(nome,cpf_cnpj,cnpj_empresa) values("{nome}","{cpf_cnpj}","{cnpj_empresa}")')

                                        curPlataform.execute(f'select * from notafiscal_contador nc where cpf_cnpj = "{condicao}"')
                                        rowsPlat=curPlataform.fetchall()
                                        rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]
                                        
                                        contador = rows_dict_plat[0]['id'] # get id contador

                                        # vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É MDFE
                                        print_log(f"Inicia select MDFE- xmlcontador")
                                        cur.execute(f"select n.numero_mdfe,n.chave,n.data_emissao,n.serie,n.fk_empresa, n.xml,  n.situacao from mdfe_master n where situacao in ('T','C') and n.data_emissao > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)")
                                        rowsNotas=cur.fetchall()
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

                                            SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)


                                        # vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É NFE
                                        print_log(f"Inicia select NFE- xmlcontador")
                                        cur.execute('select n.numero,n.chave,n.data_emissao,n.serie,n.fkempresa, n.xml,n.xml_cancelamento, n.situacao from nfe_master n where situacao in (2,3,5) and n.data_emissao > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)')
                                        rowsNotas=cur.fetchall()
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

                                            SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)
                                            
                                        # vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É NFCE
                                        print_log(f"Inicia select NFCE- xmlcontador")
                                        cur.execute(f"select n.numero,n.chave,n.data_emissao,n.serie,n.fkempresa, n.xml,n.xml_cancelamento, n.situacao from nfce_master n where situacao in ('T','C','I') and chave <> 'CHAVE NÃO GERADA' and n.data_emissao > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)")
                                        rowsNotas=cur.fetchall()
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

                                            SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)

                                        

                                        # vamos pegar todas as notas dessa empresa e salvar na plataforma - PRESTENÇÃO, É COMPRAS
                                        print_log(f"Inicia select COMPRAS- xmlcontador")
                                        cur.execute(f"select n.nr_nota,n.chave,n.dtemissao,n.serie,n.empresa, n.xml from COMPRA N WHERE N.chave is not null and n.dtemissao > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)")
                                        rowsNotas=cur.fetchall()
                                        rows_dict_notas = [dict(zip([column[0] for column in cur.description], rowNota)) for rowNota in rowsNotas]
                                        for row_nota in rows_dict_notas:
                                            numero = row_nota['NR_NOTA']
                                            chave = row_nota['CHAVE']
                                            tipo_nota = 'COMP'
                                            serie = row_nota['SERIE']
                                            data_nota = row_nota['DTEMISSAO']
                                            xml = row_nota['XML']
                                            xml_cancelamento = ''

                                            cliente_id = cnpj_empresa
                                            contador_id = contador

                                            SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)
                                            
                
                                    conMYSQL.commit()        
                                            
                            elif sistema_em_uso == '2':  # gfil
                                if pasta_compartilhada_backup != None and \
                                        caminho_base_dados_gfil != None and \
                                        caminho_gbak_firebird_gfil != None:
                                    con = fdb.conMYSQLect(
                                        host='localhost',
                                        database=caminho_base_dados_gfil,
                                        user='GFILMASTER',
                                        password='b32@m451',
                                        port=int(porta_firebird_gfil)
                                    )

                                    cur = con.cursor()
                                    # Dados do contador
                                    cur.execute(f'''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as cnpj_empresa  
                                                FROM CONTABILISTA c 
                                                    LEFT OUTER JOIN DIVERSOS d 
                                                    ON c.FILIAL  = d.FILIAL 
                                                WHERE d.CNPJ = '{cnpj}' ''')
                                    rows = cur.fetchall()
                                    rows_dict = [dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                    curPlataform = conMYSQL.cursor()  # Aqui eu crio a conexão do banco da plataforma, se liga papito
                                    for row in rows_dict:
                                        condicao = row['CPF']
                                        if condicao is None:
                                            condicao = row['CNPJ']

                                        contador = 0
                                                                
                                        curPlataform.execute(f'select * from notafiscal_contador nc where cpf_cnpj = "{condicao}"')
                                        rowsPlat=curPlataform.fetchall()
                                        rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]                            

                                        #salvo contador
                                        print_log(f"Inicia select contador - xmlcontador")
                                        if len(rowsPlat) == 0:
                                            nome = rows_dict[0]['NOME']
                                            cpf_cnpj = condicao
                                            cnpj_empresa = rows_dict[0]['CNPJ_EMPRESA'] 
                                            curPlataform.execute(f'insert into notafiscal_contador(nome,cpf_cnpj,cnpj_empresa) values("{nome}","{cpf_cnpj}","{cnpj_empresa}")')

                                        curPlataform.execute(f'select * from notafiscal_contador nc where cpf_cnpj = "{condicao}"')
                                        rowsPlat=curPlataform.fetchall()
                                        rows_dict_plat = [dict(zip([column[0] for column in curPlataform.description], rowPlat)) for rowPlat in rowsPlat]
                                        
                                        contador = rows_dict_plat[0]['id'] # get id contador


                                    

                                    # salva notas nfe
                                    cur.execute(f'''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as CNPJ_EMPRESA, DATA_EMIS_NFE,XML,XML_CANCELAM,
                                                        n.NUMERO, n.CHAVE, n.SERIE  
                                                FROM CONTABILISTA c 
                                                    LEFT OUTER JOIN DIVERSOS d 
                                                    ON c.FILIAL  = d.FILIAL 
                                                    LEFT OUTER JOIN NFE_MESTRE n 
                                                    ON n.FILIAL  = d.FILIAL 
                                                WHERE n.DATA_EMIS_NFE > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)''')
                                    
                                    rows = cur.fetchall()
                                    rows_dict = [
                                        dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                    for row_nota in rows_dict:
                                        try:
                                            XML = zlib.decompress(row_nota['XML'])
                                            XML = XML.decode('utf-8')
                                        except:
                                            print_log('Nota não existe')
                                        try:
                                            XML_CANCELAM = zlib.decompress(
                                                row_nota['XML_CANCELAM'])
                                            XML_CANCELAM = XML_CANCELAM.decode('utf-8')
                                        except:
                                            XML_CANCELAM = ''
                                            print_log('Nota cancelamento não existe')

                                        numero = row_nota['NUMERO']
                                        chave = row_nota['CHAVE']
                                        tipo_nota = 'NFE'
                                        serie = row_nota['SERIE']
                                        data_nota = row_nota['DATA_EMIS_NFE']
                                        xml = XML
                                        xml_cancelamento = XML_CANCELAM
                                        cliente_id = row_nota['CNPJ_EMPRESA']
                                        contador_id = contador

                                        SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)
                                


                                    # salva notas nfce
                                    cur.execute(f'''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as CNPJ_EMPRESA, DHEMI,XML,XML_CANCELAM,
                                                        n.NUMERO, n.CHAVE, n.SERIE  
                                                FROM CONTABILISTA c 
                                                    LEFT OUTER JOIN DIVERSOS d 
                                                    ON c.FILIAL  = d.FILIAL 
                                                    LEFT OUTER JOIN NFCE_MESTRE n 
                                                    ON n.FILIAL  = d.FILIAL 
                                                WHERE n.DHEMI > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)''')
                                    
                                    rows = cur.fetchall()
                                    rows_dict = [
                                        dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                    for row_nota in rows_dict:
                                        try:
                                            XML = zlib.decompress(row_nota['XML'])
                                            XML = XML.decode('utf-8')
                                        except:
                                            print_log('Nota não existe')
                                        try:
                                            XML_CANCELAM = zlib.decompress(
                                                row_nota['XML_CANCELAM'])
                                            XML_CANCELAM = XML_CANCELAM.decode('utf-8')
                                        except:
                                            XML_CANCELAM = ''
                                            print_log('Nota de cancelamento não existe')

                                        numero = row_nota['NUMERO']
                                        chave = row_nota['CHAVE']
                                        tipo_nota = 'NFCE'
                                        serie = row_nota['SERIE']
                                        data_nota = row_nota['DHEMI']
                                        xml = XML
                                        xml_cancelamento = XML_CANCELAM
                                        cliente_id = row_nota['CNPJ_EMPRESA']
                                        contador_id = contador

                                        SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)
                                
                                    # salva notas CTE
                                    cur.execute(f'''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as CNPJ_EMPRESA, DHEMI,XML,XML_CANCELAM,
                                                        n.NUMERO, n.CHAVE, n.SERIE  
                                                FROM CONTABILISTA c 
                                                    LEFT OUTER JOIN DIVERSOS d 
                                                    ON c.FILIAL  = d.FILIAL 
                                                    LEFT OUTER JOIN CTE_MESTRE n 
                                                    ON n.FILIAL  = d.FILIAL 
                                                WHERE n.DHEMI > dateadd(DAY,{dias_busca_nota},CURRENT_DATE)''')
                                    
                                    rows = cur.fetchall()
                                    rows_dict = [
                                        dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                    for row_nota in rows_dict:
                                        try:
                                            XML = zlib.decompress(row_nota['XML'])
                                            XML = XML.decode('utf-8')
                                        except:
                                            print_log('Nota não existe')
                                        try:
                                            XML_CANCELAM = zlib.decompress(
                                                row_nota['XML_CANCELAM'])
                                            XML_CANCELAM = XML_CANCELAM.decode('utf-8')
                                        except:
                                            XML_CANCELAM = ''
                                            print_log('Nota de cancelamento não existe')

                                        numero = row_nota['NUMERO']
                                        chave = row_nota['CHAVE']
                                        tipo_nota = 'CTE'
                                        serie = row_nota['SERIE']
                                        data_nota = row_nota['DHEMI']
                                        xml = XML
                                        xml_cancelamento = XML_CANCELAM
                                        cliente_id = row_nota['CNPJ_EMPRESA']
                                        contador_id = contador

                                        SalvaNota(conMYSQL,numero,chave,tipo_nota,serie,data_nota,xml,xml_cancelamento,cliente_id,contador_id)

                                    conMYSQL.commit() 
                time.sleep(intervalo)

            except Exception as a:
                # self.logger.error(f"{self._svc_name_} {a}.")
                conMYSQL.rollback()
                print_log(a)

