from mysql.connector import Error
import fdb
import parametros
import mysql.connector
import time
import re
import io
from PIL import Image
from funcoes import carregar_configuracoes,inicializa_conexao_firebird, inicializa_conexao_mysql_replicador, print_log

carregar_configuracoes()

inicializa_conexao_mysql_replicador('19775656000104')
nome_servico = 'Replicador'
connection_firebird = parametros.FIREBIRD_CONNECTION
connection_mysql = parametros.MYSQL_CONNECTION_REPLICADOR

#===============FIREBIRD===================

def buscar_nome_chave_primaria_firebird(tabela):
    try:
        cursor = connection_firebird.cursor()

        query_codigo = f"""
        SELECT TRIM(RDB$FIELD_NAME)
        FROM RDB$RELATION_FIELDS
        WHERE RDB$RELATION_NAME = '{tabela}' AND UPPER(RDB$FIELD_NAME) = 'CODIGO'
        """
        cursor.execute(query_codigo)
        row_codigo = cursor.fetchone()
        
        if row_codigo:
            return 'CODIGO' 
        
        # Verificar se há uma chave primária
        query = f"""
        SELECT TRIM(segments.RDB$FIELD_NAME)
        FROM RDB$RELATION_CONSTRAINTS constraints
        JOIN RDB$INDEX_SEGMENTS segments ON constraints.RDB$INDEX_NAME = segments.RDB$INDEX_NAME
        WHERE constraints.RDB$RELATION_NAME = '{tabela}'
          AND constraints.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
        """
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            return row[0]  # Retorna o nome da coluna da chave primária
         
        
        # Se não encontrar chave primária nem campo 'codigo', retornar None
        return None
        
    except Exception as e:
        print_log(f"Erro ao buscar nome da chave primária no Firebird: {e}", nome_servico)
        return None



def buscar_elemento_firebird(tabela, codigo):
    try:
        cursor = connection_firebird.cursor()

        chave_primaria = buscar_nome_chave_primaria_firebird(tabela)
        if not chave_primaria:
            print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
            return None
        
        sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = ?"

        cursor.execute(sql_select, (codigo,))

        dados = cursor.fetchone()

        if dados:
            colunas = [desc[0] for desc in cursor.description]
            dados = dict(zip(colunas, dados))

        return dados

    except fdb.fbcore.DatabaseError as e:
        print_log(f"Erro ao buscar elemento no Firebird: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()


def buscar_alteracoes_firebird():
        try:
            cursor = connection_firebird.cursor()

            cursor.execute("SELECT * FROM REPLICADOR")

            alteracoes = cursor.fetchall()

            cursor.close()
            
            return alteracoes
        
        except fdb.fbcore.DatabaseError as e:
            print_log(f"verificar alteração:{e}", nome_servico)
            connection_firebird.rollback()



def update_firebird(tabela, codigo, dados):
        try:
            cursor = connection_firebird.cursor()

            set_clause = ', '.join([f"{coluna} = ?" for coluna in dados.keys()])
            sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO = ?"

            valores = list(dados.values())
            valores.append(codigo)

            cursor.execute(sql_update, valores)

            connection_firebird.commit()
    
            cursor.close()
        except fdb.fbcore.DatabaseError as e:
            print_log(f"Erro ao atualizar dados no Firebird: {e}", nome_servico)
            connection_firebird.rollback()



def insert_firebird(tabela, dados):
        try:
            cursor = connection_firebird.cursor()

            colunas = ', '.join(dados.keys())
            placeholders = ', '.join(['?'] * len(dados))
            valores = list(dados.values())

            sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

            cursor.execute(sql_insert, valores)

            connection_firebird.commit()
            
            cursor.close()
        except fdb.fbcore.DatabaseError as e:
            print_log(f"Erro ao inserir dados no Firebird: {e}", nome_servico)
            connection_firebird.rollback()



def delete_registro_replicador(tabela, acao, chave):
    try:
        cursor = connection_firebird.cursor()

        sql_delete = "DELETE FROM REPLICADOR WHERE chave = ? AND tabela = ? AND acao = ? ROWS 1;"

        cursor.execute(sql_delete, (chave, tabela, acao))
        connection_firebird.commit()



    except fdb.fbcore.DatabaseError as e:
        print_log(f"Erro ao deletar registros da tabela REPLICADOR: {e}", nome_servico)
        connection_firebird.rollback()
        

    finally:
        if cursor:
            cursor.close()


def delete_firebird(tabela, codigo):
    try:
        cursor = connection_firebird.cursor()

        chave_primaria = buscar_nome_chave_primaria_firebird(tabela)

        sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = ?"

        cursor.execute(sql_delete, (codigo,))
        connection_firebird.commit()

    except fdb.fbcore.DatabaseError as e:
        print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
        connection_firebird.rollback()


    finally:
        if cursor:
            cursor.close()


#===============MYSQL=======================


def buscar_nome_chave_primaria_mysql(tabela):
    try:
        cursor = connection_mysql.cursor()
        
        query_codigo = f"""
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_NAME = '{tabela}'
          AND COLUMN_NAME = 'codigo'
        """
        cursor.execute(query_codigo)
        row_codigo = cursor.fetchone()
        if row_codigo:
            return 'codigo' 
        
        
        query = f"""
        SELECT COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = '{tabela}'
          AND CONSTRAINT_NAME = 'PRIMARY'
        """
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row[0]  
        
        return None
        
    except Exception as e:
        print_log(f"Erro ao buscar nome da chave primária: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()




def buscar_elemento_mysql(tabela, codigo):
    try:
        
        cursor = connection_mysql.cursor(dictionary=True)
        
        chave_primaria = buscar_nome_chave_primaria_mysql(tabela)
        
        if not chave_primaria:
            print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
            return None
        
        sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = %s"

        cursor.execute(sql_select, (codigo,))
        dados = cursor.fetchone()

        cursor.close()

        return dados

    except Exception as e:
        print_log(f"Erro ao buscar elemento MySQL: {e}", nome_servico)
        return None
 
#FUNÇÃO AUXILIAR DO INSERT E UPDATE_MYSQL
def extrair_detalhes_chave_estrangeira(erro, dados):
    match = re.search(r"FOREIGN KEY \(`(.+?)`\) REFERENCES `(.+?)` \(`(.+?)`\)", str(erro))
    if match:
        coluna_chave_estrangeira = match.group(1)
        tabela_referenciada = match.group(2)
        valor_chave_estrangeira = dados.get(coluna_chave_estrangeira)
        return tabela_referenciada, valor_chave_estrangeira
    return None, None

def verificar_tipo_coluna(tabela, dados):
    try:
        cur_fb = connection_firebird.cursor()
        for coluna in dados.keys():

            cur_fb.execute(f"SELECT RDB$FIELD_NAME, RDB$FIELD_SOURCE from rdb$relation_fields where  RDB$FIELD_NAME = '{coluna}'  and RDB$RELATION_NAME = '{tabela}'")
            field_source = cur_fb.fetchall()[0][1]

            cur_fb.execute(f"SELECT RDB$FIELD_TYPE FROM RDB$FIELDS WHERE RDB$FIELD_NAME = '{field_source}'")
            field_type = cur_fb.fetchall()[0][0]
            if field_type == 261:
                if not isinstance(dados[coluna], str):
                    if dados[coluna] != None:
                        content = dados[coluna].read()
                        # if 'xml' in content:
                        #     dados[coluna] = content
                        #     continue
                        image = Image.open(io.BytesIO(content))
                        with io.BytesIO() as output:
                            image.save(output, format="JPEG")
                            dados[coluna] = output.getvalue()
                        image.close()
        cur_fb.close()
        return dados
    except Exception as e:
        print_log(f"Erro ao verificar tipo do campo: {e}", nome_servico)

def update_mysql(tabela, codigo, dados):
        try:
            cursor = connection_mysql.cursor()

            set_clause = ', '.join([f"{coluna} = %s" for coluna in dados.keys()])
            coluna_chave_primaria = buscar_nome_chave_primaria_firebird(tabela)
            sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s"
            dados = verificar_tipo_coluna(tabela, dados)
            valores = list(dados.values())
            valores.append(codigo)
            
            cursor.execute(sql_update, valores)

            connection_mysql.commit()
            
            cursor.close()
        except Error as e:
            print_log(f"Erro ao atualizar dados no MySQL: {e}", nome_servico)
            connection_mysql.rollback()

            if "foreign key constraint fails" in str(e).lower():
                tabela_referenciada, valor_chave_estrangeira = extrair_detalhes_chave_estrangeira(e, dados)

            if tabela_referenciada and valor_chave_estrangeira:
            
                elemento_firebird = buscar_elemento_firebird(tabela_referenciada, valor_chave_estrangeira)

                #inserir dados para o relacionamento funcionar
                insert_mysql(tabela_referenciada, elemento_firebird)

                #tentar update dados do começo
                update_mysql(tabela,dados)


def insert_mysql(tabela, dados):
    try:
        cursor_mysql = connection_mysql.cursor()

        colunas = ', '.join(dados.keys())
        placeholders = ', '.join(["%s"] * len(dados))
        dados = verificar_tipo_coluna(tabela, dados)
        valores = list(dados.values())

        sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

        cursor_mysql.execute(sql_insert, valores)

        connection_mysql.commit()
        
        cursor_mysql.close()
    except mysql.connector.Error as e:
        print_log(f"Erro ao inserir dados no MySQL: {e}", nome_servico)
        connection_mysql.rollback()

        #caso não ter o elemento para o relacionamento
        if "foreign key constraint fails" in str(e).lower():
            print_log("Sera adicionado elemento de chave estrangeira...", nome_servico)
            tabela_referenciada, valor_chave_estrangeira = extrair_detalhes_chave_estrangeira(e, dados)
            if tabela_referenciada and valor_chave_estrangeira:
            
                elemento_firebird = buscar_elemento_firebird(tabela_referenciada, valor_chave_estrangeira)

                #inserir dados para o relacionamento funcionar
                insert_mysql(tabela_referenciada, elemento_firebird)

                #tentar inserir dados do começo
                insert_mysql(tabela,dados)

def buscar_relacionamentos(tabela):
    try:
        cursor = connection_mysql.cursor(dictionary=True)
        
        query = f"""
        SELECT TABLE_NAME, COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME = '{tabela}'
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        relacionamentos = []
        for resultado in resultados:
            tabela_origem = resultado['TABLE_NAME']
            coluna_origem = resultado['COLUMN_NAME']
            relacionamentos.append((tabela_origem, coluna_origem))
        
        return relacionamentos
        
    except Error as e:
        print_log(f"Erro ao buscar relacionamentos da tabela {tabela}: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()

def delete_relacionamento_mysql(tabela, codigo, chave_estrageira):
        try:
            cursor = connection_mysql.cursor()


            sql_delete = f"DELETE FROM {tabela} WHERE {chave_estrageira} = {codigo}"
            cursor.execute(sql_delete)

            connection_mysql.commit()
            
            cursor.close()
        except Error as e:
            print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
            connection_mysql.rollback()



def delete_mysql(tabela, codigo):
        try:
            cursor = connection_mysql.cursor()

            chave_primaria = buscar_nome_chave_primaria_mysql(tabela)

            sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = {codigo}"
            cursor.execute(sql_delete)

            connection_mysql.commit()
            
            cursor.close()
        except Error as e:
            print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
            connection_mysql.rollback()
            if "foreign key constraint fails" in str(e).lower():
                informacao_relacionamento = buscar_relacionamentos(tabela)

                tabela_relacionamento = informacao_relacionamento[0][0]
                campo_relacionamento = informacao_relacionamento[0][1]

                delete_relacionamento_mysql(tabela_relacionamento, codigo, campo_relacionamento)

#====================processamento da aplicação=============================

def processar_alteracoes():

    alteracoes = buscar_alteracoes_firebird()


    for alteracao in alteracoes:
        
        tabela = alteracao[0].upper()
        acao = alteracao[1].upper()
        valor = alteracao[2]
        
        existe_elemento_mysql = buscar_elemento_mysql(tabela,valor)
        elemento_firebird = buscar_elemento_firebird(tabela, valor)


#       SE JÁ EXISTE ESSE ELEMENTO NO MYSQL
        if existe_elemento_mysql:
            if acao == "I":
                update_mysql(tabela, valor, elemento_firebird)

            elif acao == "U":
                update_mysql(tabela, valor, elemento_firebird)

            elif acao == "D":
                delete_mysql(tabela, valor)


#       SE NÃO EXISTE ESSE ELEMENTO NO MYSQL
        elif not existe_elemento_mysql and elemento_firebird:
            if acao == "I":
                insert_mysql(tabela, elemento_firebird)

            elif acao == "U":
                insert_mysql(tabela, elemento_firebird)
                 

        delete_registro_replicador(tabela, acao, valor)
     

#=======LOOP=========

while True:
    
    print_log('Executando.....', nome_servico)
    processar_alteracoes()
    print_log('Alterações executadas.... esperando 10 segundos...', nome_servico)
    time.sleep(10)


        
