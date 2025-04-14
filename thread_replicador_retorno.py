import fdb
import parametros
import mysql.connector
import re
import os
import sys
import datetime
from funcoes import inicializa_conexao_mysql_replicador, inicializa_conexao_firebird,print_log, pode_executar, criar_bloqueio, remover_bloqueio, caminho_bd, verifica_dll_firebird

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

def buscar_nome_chave_primaria(tabela: str) -> str|None:
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


def buscar_elemento_firebird(tabela:str, codigo:int, codigo_global: int = 0) -> dict|None:
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



def update_firebird(tabela: str, codigo: int, dados: dict,  codigo_global: int = 0) -> None:
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


def insert_firebird(tabela: str, dados: dict) -> None:
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

def delete_firebird(tabela: str, codigo: int, codigo_global: int = 0) -> None:
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

def firebird_mysql() -> None:

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