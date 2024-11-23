from mysql.connector import Error
import fdb
import mysql.vendor
import mysql.vendor.plugin
import parametros
import mysql.connector
import re
import time
import os
import sys
from funcoes import carregar_configuracoes, inicializa_conexao_mysql_replicador, print_log, pode_executar, criar_bloqueio, remover_bloqueio

#===============FIREBIRD===================
def verifica_empresa_firebird(conn, dados: dict) -> tuple[int, str]:
    cursor = conn.cursor()
    codigo_empresa = 0
    for coluna, valor in dados.items():
        if 'EMPRESA' in coluna.upper():
            if isinstance(valor, int):
                codigo_empresa = valor
                break
        elif 'EMITENTE' in coluna.upper():
            if isinstance(valor, int):
                codigo_empresa = valor
                break
    cnpj = ''
    if codigo_empresa > 0:
        try:
            cursor.execute(f'SELECT CNPJ FROM EMPRESA WHERE CODIGO = {codigo_empresa}')
            cnpj = cursor.fetchall()[0][0]
        except Exception as e:
            print_log(f'Nao foi possivel consultar empresa: {e}', nome_servico)

    return codigo_empresa, cnpj

def buscar_nome_chave_primaria(tabela):
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


def buscar_elemento_firebird(tabela:str, codigo:int, envio:bool=True):
    try:
        cursor = connection_firebird.cursor()

        chave_primaria = buscar_nome_chave_primaria(tabela)
        if not chave_primaria:
            print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
            return None
        
        sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = ?"

        cursor.execute(sql_select, (codigo,))

        dados = cursor.fetchone()

        if dados:
            colunas = [desc[0] for desc in cursor.description]
            dados = dict(zip(colunas, dados))
        else:
            print_log(f'Não há elemento Firebird com esta chave - chave: {codigo} (pode ter sido excluido ou precisa ser adicionado!)')

        return dados

    except Exception as e:
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
        #TODO: Corrigir update local
        try:
            cursor = connection_firebird.cursor()

            set_clause = ', '.join([f"{coluna} = ?" for coluna in dados.keys()])
            sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO = ?"

            valores = isblob(dados)
            valores.append(codigo)
            
            print_log(f'Update na tabela {tabela} -> chave: {codigo}')
            cursor.execute(sql_update, valores)

            connection_firebird.commit()
    
            cursor.close()
        except Exception as e:
            print_log(f"Erro ao atualizar dados no Firebird: {e}", nome_servico)
            connection_firebird.rollback()


def insert_firebird(tabela, dados):
        #TODO: Corrigir insert local
        try:
            cursor = connection_firebird.cursor()

            colunas = ', '.join(dados.keys())
            placeholders = ', '.join(['?'] * len(dados))
            valores = isblob(dados)

            sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

            print_log(f'Insert na tabela {tabela}')
            cursor.execute(sql_insert, valores)

            connection_firebird.commit()
            
            cursor.close()
        except fdb.fbcore.DatabaseError as e:
            print_log(f"Erro ao inserir dados no Firebird: {e}", nome_servico)
            connection_firebird.rollback()

def delete_firebird(tabela, codigo):
    #TODO: Corrigir delete local
    try:
        cursor = connection_firebird.cursor()

        chave_primaria = buscar_nome_chave_primaria(tabela)

        sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = ?"

        print_log(f'Delete na tabela: {tabela} -> chave: {codigo}')
        cursor.execute(sql_delete, (codigo,))
        connection_firebird.commit()

    except fdb.fbcore.DatabaseError as e:
        print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
        connection_firebird.rollback()


    finally:
        if cursor:
            cursor.close()


#===============AUX=========================

def consulta_cnpjs_local() -> list | None:
    try:
        cursor = connection_firebird.cursor()
        cursor.execute('SELECT CODIGO, CNPJ FROM EMPRESA')
        empresas = cursor.fetchall()
        cursor.close()
        if not empresas:
            return None
        return empresas
    except Exception as e:
        print_log(f'Erro ao consultar os cnpjs locais -> motivo: {e}')

def isblob(dados: dict):
    valores = []
    for key, valor in dados.items():
        if isinstance(valor, fdb.fbcore.BlobReader):  # Verifica se o valor é BLOB
            blob = valor.read()
            # str_blob = blob.decode('ISO_8859_1')
            valores.append(blob)  # Adiciona o BLOB diretamente
            valor.close()
        else:
            valores.append(valor)  # Adiciona os outros valores
    return valores

def delete_registro_replicador(tabela, acao, chave, firebird=True):

    if firebird:
        try:

            sql_delete = "DELETE FROM REPLICADOR WHERE chave = ? AND tabela = ? AND acao = ? ROWS 1;"
            cursor = connection_firebird.cursor()

            cursor.execute(sql_delete, (chave, tabela, acao,))

            connection_firebird.commit()

        except fdb.fbcore.DatabaseError as e:
            print_log(f"Erro ao deletar registros da tabela REPLICADOR: {e}", nome_servico)
            connection_firebird.rollback()
            
        finally:
            if cursor:
                cursor.close()
    else:
        try:

            sql_delete = "DELETE FROM REPLICADOR WHERE CHAVE = %s AND TABELA = %s AND ACAO = %s LIMIT 1;"
            cursor = connection_mysql.cursor()

            cursor.execute(sql_delete, (chave, tabela, acao,))

            connection_mysql.commit()

        except Exception as e:
            print_log(f"Erro ao deletar registros da tabela REPLICADOR: {e}", nome_servico)

        finally:
            if cursor:
                cursor.close()

#===============MYSQL=======================

def buscar_alteracoes_replicador_mysql(empresas: list) -> list:
    try:
        alteracoes = []
        if empresas != None:
            cursor_mysql = connection_mysql.cursor()
            for codigo, cnpj in empresas:
                cursor_mysql.execute(f'SELECT * FROM REPLICADOR WHERE CNPJ_EMPRESA = {cnpj}')
                result = cursor_mysql.fetchall()
                alteracoes += result
            cursor_mysql.close()
        return alteracoes
    except Exception as e:
        print_log(f"Verificar alteracao: {e}")


def verifica_campo_chave_primaria_mysql(tabela: str):
    try:
        cursor = parametros.MYSQL_CONNECTION_REPLICADOR.cursor()
        sql = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = 'dados'
                            AND UPPER(TABLE_NAME) = UPPER('{tabela}') 
                            AND  UPPER(COLUMN_NAME) = UPPER('CODIGO_GLOBAL')"""
        cursor.execute(sql)
        chave = cursor.fetchone()

        if len(chave) <= 0:
            sql_alt = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = 'dados'
                            AND UPPER(TABLE_NAME) = UPPER('{tabela}') 
                            AND  (UPPER(COLUMN_NAME) = UPPER('CODIGO')
                            OR UPPER(COLUMN_NAME) = upper('CNPJ_EMPRESA'))"""
            cursor.execute(sql_alt)
            chave = cursor.fetchone()

        if len(chave) <= 0:
            chave = None

        return chave

    except Exception as e:
        print(f'Não foi possivel buscar chave primaria da tabela: {tabela} - motivo: {e}')

def buscar_valor_chave_primaria(tabela):
    try:

        tipo_campo = verifica_campo_chave_primaria_mysql(tabela)

        if not tipo_campo:
            return None
        elif len(tipo_campo) == 1:
            sql = f'SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = ?'

    except Exception as e:
        print_log(f'Erro ao buscar valor da chave primaria - tabela: {tabela} -> motivo: {e}')

    return

def buscar_elemento_mysql(tabela: str, codigo: int, codigo_global: int = 0) -> dict | None:
    try:
        
        cursor = connection_mysql.cursor(dictionary=True)
        if codigo_global:
            sql_select = f"SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = %s"
            cursor.execute(sql_select, (codigo_global,))
        else:
            chave_primaria = buscar_nome_chave_primaria(tabela)
            if not chave_primaria:
                print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                return None
        
            sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = %s"
            cursor.execute(sql_select, (codigo,))

        dados = cursor.fetchone()

        if dados == None:
            print_log(f'Não há elemento que possua esta chave no Mysql - chave: {codigo} ou este código global: {codigo_global}', nome_servico)
            return None
        
        dados = dict(dados)
        dados.pop('CNPJ_EMPRESA')

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

def update_mysql(tabela: str, codigo: int, dados: dict):
        try:
            cursor = connection_mysql.cursor()
            set_clause = ', '.join([f"{coluna} = %s" for coluna in dados.keys()])
            valores = isblob(dados)
            codigo_empresa, cnpj = verifica_empresa_firebird(connection_firebird, dados)

            coluna_chave_primaria = buscar_nome_chave_primaria(tabela)
            if cnpj:
                set_clause += ', CNPJ_EMPRESA = %s'
                valores.append(cnpj)
                if dados['CODIGO_GLOBAL']:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO_GLOBAL = {dados['CODIGO_GLOBAL']}"
                else:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s AND CNPJ_EMPRESA = %s"
                    valores.append(codigo)
                    valores.append(cnpj)
            else:
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s AND CNPJ_EMPRESA = %s"
                valores.append(codigo)
                valores.append(cnpj)
            
            print_log(f'Update na tabela {tabela} -> chave: {codigo} -> cnpj:{cnpj}', nome_servico)
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
                update_mysql(tabela, codigo,dados)

def insert_mysql(tabela: str, dados: dict):
    try:
        cursor_mysql = connection_mysql.cursor()
        dados.pop('CODIGO_GLOBAL')
        valores = isblob(dados)

        codigo_empresa, cnpj = verifica_empresa_firebird(connection_firebird, dados)
        if cnpj:
            colunas = ', '.join(dados.keys())
            colunas += ', CNPJ_EMPRESA'
            placeholders = ', '.join(["%s"] * (len(dados) + 1))
            valores.append(cnpj)
        else:
            colunas = ', '.join(dados.keys())
            placeholders = ', '.join(["%s"] * len(dados))

        sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

        print_log(f'Insert na tabela {tabela} -> CNPJ: {cnpj}', nome_servico)
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

            chave_primaria = buscar_nome_chave_primaria(tabela)

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

    print_log('Iniciando processamento de alteracoes...', nome_servico)
    
    firebird_mysql()
    mysql_firebird()

    
     
def firebird_mysql():

    print_log('Iniciando Envio de dados...')

    alteracoes_firebird = buscar_alteracoes_firebird()


    for alteracao in alteracoes_firebird:
        
        tabela = alteracao[0].upper()
        acao = alteracao[1].upper()
        valor = alteracao[2]
        
        elemento_firebird = buscar_elemento_firebird(tabela, valor)
        existe_elemento_mysql = buscar_elemento_mysql(tabela, valor, elemento_firebird['CODIGO_GLOBAL'])

        if elemento_firebird is None:
            delete_registro_replicador(tabela, acao, valor)
            continue

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

def mysql_firebird():

    print_log('Iniciando Recebimento de dados...')

    empresas = consulta_cnpjs_local()

    alteracoes_mysql = buscar_alteracoes_replicador_mysql(empresas)

    for alteracao in alteracoes_mysql:
        
        tabela = alteracao[0].upper()
        acao = alteracao[1].upper()
        valor = alteracao[2]
        codigo_global = alteracao[4]
        
        elemento_mysql = buscar_elemento_mysql(tabela, valor, codigo_global)
        existe_elemento_firebird = buscar_elemento_firebird(tabela, valor, False)

        # SE JA EXISTE ELEMENTO FIREBIRD
        if existe_elemento_firebird:
            if acao == "I":
                update_firebird(tabela, valor, elemento_mysql)
            elif acao == "U":
                update_firebird(tabela, valor, elemento_mysql)
            elif acao == "D":
                delete_firebird(tabela, valor)

        # SE NÃO EXISTE ELEMENTO FIREBIRD
        elif not existe_elemento_firebird and elemento_mysql:
            if acao == "I":
                insert_firebird(tabela, elemento_mysql)
            if acao == "U":
                insert_firebird(tabela, elemento_mysql)

        delete_registro_replicador(tabela, acao, valor, firebird=False)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            carregar_configuracoes()
            nome_servico = 'thread_replicador'
            connection_firebird = parametros.FIREBIRD_CONNECTION

            inicializa_conexao_mysql_replicador('dados')
            connection_mysql = parametros.MYSQL_CONNECTION_REPLICADOR

            while True:
                processar_alteracoes()

                print('Esperando 10 segundos....')
                time.sleep(10)
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar: {e}', nome_script)
        finally:
            remover_bloqueio(nome_script)