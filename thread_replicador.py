import fdb
import mysql.vendor
import mysql.vendor.plugin
import parametros
import mysql.connector
import re
import os
import sys
import datetime
import configparser
from mysql.connector import Error
from funcoes import inicializa_conexao_mysql_replicador, inicializa_conexao_firebird,print_log, pode_executar, criar_bloqueio, remover_bloqueio, caminho_bd, verifica_dll_firebird

#===============FIREBIRD===================
def verifica_empresa_firebird(conn: fdb.Connection, tabela:str, dados: dict) -> tuple[int, str]:
    cursor = conn.cursor()
    codigo_empresa = 0
    if tabela == 'EMPRESA':
        codigo_empresa = dados['CODIGO']
    else:
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

def buscar_nome_chave_primaria(tabela: str):
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


def buscar_elemento_firebird(tabela:str, codigo:int, codigo_global: int = 0):
    try:
        cursor = connection_firebird.cursor()

        if codigo_global:
            sql_select = f'SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = {codigo_global}'
            cursor.execute(sql_select)
            dados = cursor.fetchone()

            if not dados:
                chave_primaria = buscar_nome_chave_primaria(tabela)
                if not chave_primaria:
                    print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                    return None
                
                if not codigo:
                    return None

                sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{codigo}'"
                cursor.execute(sql_select)
                dados = cursor.fetchone()
        else:
            chave_primaria = buscar_nome_chave_primaria(tabela)

            if not chave_primaria:
                print_log(f"Chave primária não encontrada para a tabela {tabela}.", nome_servico)
                return None
            
            sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{codigo}'"

            cursor.execute(sql_select)

            dados = cursor.fetchone()

        if dados:
            colunas = [desc[0] for desc in cursor.description]
            dados = dict(zip(colunas, dados))
        else:
            print_log(f'Não há elemento Firebird com esta chave - chave: {codigo} (pode ter sido excluido ou precisa ser adicionado!)', nome_servico)

        return dados

    except Exception as e:
        print_log(f"Erro ao buscar elemento no Firebird: {e}", nome_servico)
        return None
    finally:
        if cursor:
            cursor.close()


def buscar_alteracoes_firebird() -> list[dict | None]:
        try:

            cursor = connection_firebird.cursor()
            cursor.execute("SELECT * FROM REPLICADOR")
            alteracoes = cursor.fetchall()

            if not alteracoes:
                return []

            colunas = [coluna[0] for coluna in cursor.description]
            alteracoes_dict = [dict(zip(colunas, linha)) for linha in alteracoes]
    
            return alteracoes_dict
        except Exception as e:
            print_log(f"verificar alteração:{e}", nome_servico)
            connection_firebird.rollback()
        finally:
            if cursor:
                cursor.close()



def update_firebird(tabela: str, codigo: int, dados: dict,  codigo_global: int = 0):
        try:
            cursor = connection_firebird.cursor()
            set_clause = ', '.join([f"{coluna} = ?" for coluna in dados.keys()])
            chave_primaria = buscar_nome_chave_primaria(tabela)

            if codigo:
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {chave_primaria} = ?"
                valores = tratar_valores(dados)
                valores.append(codigo)

            elif codigo_global:
                codigo = verifica_valor_chave_primaria(tabela, codigo_global, chave_primaria)
                dados[chave_primaria] = codigo
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO_GLOBAL = ?"
                valores = tratar_valores(dados)
                valores.append(codigo_global)

            else:
                return
 
            print_log(f'Update na tabela {tabela} -> chave: {codigo} ou codigo global: {codigo_global}\n', nome_servico)
            cursor.execute(sql_update, valores)

            connection_firebird.commit()
        except Exception as e:
            print_log(f"Erro ao atualizar dados no Firebird: {e}", nome_servico)
            connection_firebird.rollback()
        finally:
            if cursor:
                cursor.close()


def insert_firebird(tabela: str, dados: dict):
    try:

        cursor = connection_firebird.cursor()

        if tabela.lower() == 'vendas_detalhe':
            codigo_master = dados['CODIGO_GLOBAL_MASTER']
            cursor.execute(f'select codigo from vendas_master where codigo_global = {codigo_master}')
            codigo = cursor.fetchone()[0]
            dados['FKVENDA'] = codigo

        colunas = ', '.join(dados.keys())
        placeholders = ', '.join(['?'] * len(dados))
        valores = tratar_valores(dados)
        campo_chave_primaria = buscar_nome_chave_primaria(tabela)

        sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders}) RETURNING {campo_chave_primaria}"

        print_log(f'Insert na tabela {tabela}', nome_servico)
        cursor.execute(sql_insert, valores)
        valor_chave_primaria = cursor.fetchone()[0]
        connection_firebird.commit()

        # tratamento para retorno do valor da chave primaria gerada em banco firebird local
        codigo_global = dados['CODIGO_GLOBAL']
        try:
            cursor_mysql = connection_mysql.cursor()
            sql_update_retorno = f'UPDATE {tabela} SET {campo_chave_primaria} = {valor_chave_primaria} WHERE CODIGO_GLOBAL = {codigo_global}'
            cursor_mysql.execute(sql_update_retorno)
            connection_mysql.commit()
            print_log(f'Valor de chave primaria retornado: {valor_chave_primaria} \n', nome_servico)
        except Exception as e:
            print_log(f'Erro ao retornar valor de chave primaria: {e} \n', nome_servico)
            connection_mysql.rollback()
        finally:
            if cursor_mysql:
                cursor_mysql.close()

    except Exception as e:
        print_log(f"Erro ao inserir dados no Firebird: {e}", nome_servico)
        connection_firebird.rollback()
    finally:
        if cursor:
            cursor.close()

def delete_firebird(tabela: str, codigo: int, codigo_global: int = 0):
    try:

        cursor = connection_firebird.cursor()
        if codigo_global:
            sql_delete = f"DELETE FROM {tabela} WHERE CODIGO_GLOBAL = {codigo_global}"
        elif codigo:
            chave_primaria = buscar_nome_chave_primaria(tabela)
            sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = {codigo}"
        else:
            return

        print_log(f'Delete na tabela: {tabela} -> chave: {codigo} ou codigo global: {codigo_global}', nome_servico)
        cursor.execute(sql_delete)
        connection_firebird.commit()

    except Exception as e:
        print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
        connection_firebird.rollback()
    finally:
        if cursor:
            cursor.close()


#===============AUX=========================

def verifica_valor_chave_primaria(tabela, codigo_global, chave_primaria):
    elemento = buscar_elemento_firebird(tabela, None, codigo_global)
    return elemento.get(chave_primaria, None)

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

def tratar_valores(dados: dict) -> list:
    valores = []
    for key, valor in dados.items():
        if isinstance(valor, fdb.fbcore.BlobReader):  # Verifica se o valor é BLOB
            blob = valor.read()
            valores.append(blob)
            valor.close()

        elif isinstance(valor, datetime.timedelta): # Converte tempo de segundos para hora : minuto : segundo
            total_de_segundos = valor.total_seconds()
            horas = int(total_de_segundos // 3600)
            segundos_restantes = total_de_segundos % 3600
            minutos = int(segundos_restantes // 60)
            segundos_restantes = segundos_restantes % 60
            valor = datetime.time(hour=horas, minute=minutos, second=int(segundos_restantes))
            valores.append(valor)

        else:
            valores.append(valor)  # Adiciona os outros valores
    return valores

def delete_registro_replicador(tabela, acao, chave, codigo_global=0, firebird=True):

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

            if codigo_global:
                sql_delete = "DELETE FROM REPLICADOR WHERE TABELA = %s AND ACAO = %s AND CODIGO_GLOBAL = %s LIMIT 1;"
                valores = tabela, acao, codigo_global
            else:
                sql_delete = "DELETE FROM REPLICADOR WHERE CHAVE = %s AND TABELA = %s AND ACAO = %s LIMIT 1;"
                valores = chave, tabela, acao

            cursor = connection_mysql.cursor()
            cursor.execute(sql_delete, valores)

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
        print_log(f"Verificar alteracao: {e}", nome_servico)


def buscar_elemento_mysql(tabela: str, codigo: int, cnpj: str ='', codigo_global = None) -> dict | None:
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
            
            sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = %s AND CNPJ_EMPRESA = %s"
            cursor.execute(sql_select, (codigo, cnpj))

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
    finally:
        if cursor:
            cursor.close()
 
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
            codigo_global = dados['CODIGO_GLOBAL']
            dados.pop('CODIGO_GLOBAL')
            set_clause = ', '.join([f"{coluna} = %s" for coluna in dados.keys()])
            valores = tratar_valores(dados)
            codigo_empresa, cnpj = verifica_empresa_firebird(connection_firebird, tabela, dados)

            coluna_chave_primaria = buscar_nome_chave_primaria(tabela)
            if cnpj:
                set_clause += ', CNPJ_EMPRESA = %s'
                valores.append(cnpj)
                if codigo_global:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO_GLOBAL = {codigo_global}"
                else:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s AND CNPJ_EMPRESA = %s"
                    valores.append(codigo)
                    valores.append(cnpj)
            else:
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s"
                valores.append(codigo)
            
            print_log(f'Update na tabela {tabela} -> chave: {codigo} -> cnpj:{cnpj}\n', nome_servico)
            cursor.execute(sql_update, valores)

            connection_mysql.commit()
        except Error as e:
            print_log(f"Erro ao atualizar dados no MySQL: {e}", nome_servico)
            connection_mysql.rollback()

            if "foreign key constraint fails" in str(e).lower():
                tabela_referenciada, valor_chave_estrangeira = extrair_detalhes_chave_estrangeira(e, dados)
            else:
                return

            if tabela_referenciada and valor_chave_estrangeira:
            
                elemento_firebird = buscar_elemento_firebird(tabela_referenciada, valor_chave_estrangeira)

                #inserir dados para o relacionamento funcionar
                insert_mysql(tabela_referenciada, elemento_firebird)

                #tentar update dados do começo
                update_mysql(tabela, codigo,dados)
        finally:
            if cursor:
                cursor.close()

def insert_mysql(tabela: str, dados: dict, valor: str):
    try:

        cursor = connection_mysql.cursor()
        dados.pop('CODIGO_GLOBAL')
        valores = tratar_valores(dados)
        codigo_empresa, cnpj = verifica_empresa_firebird(connection_firebird, tabela, dados)

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
        cursor.execute(sql_insert, valores)
        codigo_global = cursor._last_insert_id
        connection_mysql.commit()

        # tratamento para retornar o código global gerado no banco mysql
        try:
            campo_chave_primaria = buscar_nome_chave_primaria(tabela)
            cur_fb = connection_firebird.cursor()
            sql_update_retorno = f'UPDATE {tabela} SET CODIGO_GLOBAL = {codigo_global} WHERE {campo_chave_primaria} = {valor}'
            cur_fb.execute(sql_update_retorno)
            connection_firebird.commit()
            print_log(f'Retornou codigo global: {codigo_global}\n', nome_servico)
        except Exception as e:
            print_log(f'Nao foi possivel retornar codigo global -> motivo: {e}\n', nome_servico)
            connection_firebird.rollback()
        finally:
            if cur_fb:
                cur_fb.close()

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
    finally:
        if cursor:
            cursor.close()

def buscar_relacionamentos(tabela: str) -> list:
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

def delete_relacionamento_mysql(tabela: str, codigo: int, chave_estrageira: str):
    try:
        cursor = connection_mysql.cursor()

        sql_delete = f"DELETE FROM {tabela} WHERE {chave_estrageira} = {codigo}"
        cursor.execute(sql_delete)

        connection_mysql.commit()
    except Error as e:
        print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
        connection_mysql.rollback()
    finally:
        if cursor:
            cursor.close()



def delete_mysql(tabela: str, codigo: int):
    try:
        cursor = connection_mysql.cursor()
        empresas = consulta_cnpjs_local()
        if empresas:
            cnpj = empresas[0][1]
        chave_primaria = buscar_nome_chave_primaria(tabela)

        if not cnpj:
            return

        print_log(f"Delete na tabela {tabela} -> chave: {codigo}\n", nome_servico)
        sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = {codigo} and CNPJ_EMPRESA={cnpj}"
        cursor.execute(sql_delete)

        connection_mysql.commit()
    except Error as e:
        print_log(f"Erro ao deletar registro da tabela {tabela}: {e}", nome_servico)
        connection_mysql.rollback()
        if "foreign key constraint fails" in str(e).lower():
            informacao_relacionamento = buscar_relacionamentos(tabela)

            tabela_relacionamento = informacao_relacionamento[0][0]
            campo_relacionamento = informacao_relacionamento[0][1]

            delete_relacionamento_mysql(tabela_relacionamento, codigo, campo_relacionamento)
    finally:
        if cursor:
            cursor.close()

#====================processamento da aplicação=============================

def processar_alteracoes():

    print_log('Iniciando processamento de alteracoes...', nome_servico)
    firebird_mysql()
    mysql_firebird()

    
     
def firebird_mysql():

    print_log('Iniciando Envio de dados...', nome_servico)

    alteracoes_firebird = buscar_alteracoes_firebird()


    for alteracao in alteracoes_firebird:
        if not alteracao:
            continue
        
        tabela = alteracao['TABELA'].upper()
        acao = alteracao['ACAO'].upper()
        valor = alteracao['CHAVE']

        print_log(f'Alteração realizada: tabela -> {tabela}, acao -> {acao}, chave -> {valor}', nome_servico)
        
        elemento_firebird = buscar_elemento_firebird(tabela, valor)

        if elemento_firebird is None and (acao != 'D'):
            delete_registro_replicador(tabela, acao, valor)
            continue

        if elemento_firebird is not None:
            codigo_empresa, cnpj = verifica_empresa_firebird(connection_firebird, tabela, elemento_firebird)
            existe_elemento_mysql = buscar_elemento_mysql(tabela, valor, cnpj, elemento_firebird['CODIGO_GLOBAL'])
        else:
            empresas = consulta_cnpjs_local()
            if empresas:
                cnpj = empresas[0][1]
                existe_elemento_mysql = buscar_elemento_mysql(tabela, valor, cnpj)
            else:
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
                insert_mysql(tabela, elemento_firebird, valor)

            elif acao == "U":
                insert_mysql(tabela, elemento_firebird, valor)
                 
        delete_registro_replicador(tabela, acao, valor)

def mysql_firebird():

    print_log('Iniciando Recebimento de dados...', nome_servico)

    empresas = consulta_cnpjs_local()

    alteracoes_mysql = buscar_alteracoes_replicador_mysql(empresas)

    for alteracao in alteracoes_mysql:
        
        tabela = alteracao[0].upper()
        acao = alteracao[1].upper()
        valor = alteracao[2]
        cnpj = alteracao[3]
        codigo_global = alteracao[4]

        print_log(f'Alteração realizada: tabela -> {tabela}, acao -> {acao}, chave -> {valor}, global -> {codigo_global}', nome_servico)
        
        elemento_mysql = buscar_elemento_mysql(tabela=tabela, codigo=valor, cnpj=cnpj, codigo_global=codigo_global)
        existe_elemento_firebird = buscar_elemento_firebird(tabela, valor, codigo_global)

        # SE JA EXISTE ELEMENTO FIREBIRD
        if existe_elemento_firebird:
            if acao == "I":
                update_firebird(tabela, valor, elemento_mysql, codigo_global)
            elif acao == "U":
                update_firebird(tabela, valor, elemento_mysql, codigo_global)
            elif acao == "D":
                delete_firebird(tabela, codigo_global, valor)

        # SE NÃO EXISTE ELEMENTO FIREBIRD
        elif not existe_elemento_firebird and elemento_mysql:
            if acao == "I":
                insert_firebird(tabela, elemento_mysql)
            if acao == "U":
                insert_firebird(tabela, elemento_mysql)

        if elemento_mysql is not None:
            delete_registro_replicador(tabela, acao, valor, elemento_mysql['CODIGO_GLOBAL'], firebird=False)
        else:
            delete_registro_replicador(tabela, acao, valor, firebird=False)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    # caminho_sistema = os.path.dirname(os.path.abspath(__file__)) + '/'
    # caminho_sistema = caminho_sistema.lower().replace('server','')
    client_dll = verifica_dll_firebird()

    parametros.DATABASEFB = caminho_bd()[0]

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            inicializa_conexao_firebird(client_dll)
            inicializa_conexao_mysql_replicador()
            nome_servico = 'thread_replicador'
            connection_firebird = parametros.FIREBIRD_CONNECTION
            connection_mysql = parametros.MYSQL_CONNECTION_REPLICADOR
            
            processar_alteracoes()

            print_log('Processamento finalizando', nome_script)
            if not connection_firebird.closed:
                connection_firebird.close()
                
            if connection_mysql.is_connected():
                connection_mysql.close()
                
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar: {e}', nome_script)
        finally:
            remover_bloqueio(nome_script)