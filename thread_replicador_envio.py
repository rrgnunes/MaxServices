import parametros
import mysql.connector
import re
import os
import sys
from mysql.connector import Error
from funcoes import (
    inicializa_conexao_mysql_replicador,
    inicializa_conexao_firebird,
    verifica_dll_firebird,
    caminho_bd,
    print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    tratar_valores,
    verifica_empresa_firebird,
    buscar_nome_chave_primaria,
    buscar_elemento_firebird,
    buscar_elemento_mysql,
    consulta_cnpjs_local,
    delete_registro_replicador
    )

def buscar_alteracoes_firebird():
    """
    Busca os registros alterados no banco de dados local
    """
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

def update_mysql(tabela: str, codigo: int, dados: dict):
    """
    Atualiza o registro remoto de acordo com a alteração feita no banco local
    """
    try:
        cursor = connection_mysql.cursor()
        codigo_global = dados['CODIGO_GLOBAL']
        dados.pop('CODIGO_GLOBAL')
        set_clause = ', '.join([f"{coluna} = %s" for coluna in dados.keys()])
        valores = tratar_valores(dados)
        codigo_empresa, cnpj = verifica_empresa_firebird(tabela, dados)

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
    """
    Insere no banco remoto o registro criado no banco local
    """
    try:

        cursor = connection_mysql.cursor()
        dados.pop('CODIGO_GLOBAL')
        valores = tratar_valores(dados)
        codigo_empresa, cnpj = verifica_empresa_firebird(tabela, dados)

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

def delete_mysql(tabela: str, codigo: int):
    """
    Deleta a registro do banco remoto de acordo com o registro deletado no banco local
    """
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

def buscar_relacionamentos(tabela: str):
    """
    Busca registro vinculado (via chave estrangeira) ao registro sendo enviado ao banco remoto
    """
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
    """
    Deleta o registro do banco remoto de acordo com o registro deletado no banco local
    """
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


#FUNÇÃO AUXILIAR DO INSERT E UPDATE_MYSQL
def extrair_detalhes_chave_estrangeira(erro, dados):
    match = re.search(r"FOREIGN KEY \(`(.+?)`\) REFERENCES `(.+?)` \(`(.+?)`\)", str(erro))
    if match:
        coluna_chave_estrangeira = match.group(1)
        tabela_referenciada = match.group(2)
        valor_chave_estrangeira = dados.get(coluna_chave_estrangeira)
        return tabela_referenciada, valor_chave_estrangeira
    return None, None

def firebird_mysql():
    """
    Loop Principal sobre os registros alterados no banco local
    """

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
            codigo_empresa, cnpj = verifica_empresa_firebird(tabela, elemento_firebird)
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

if __name__ == '__main__':

    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_servico):
        criar_bloqueio(nome_servico)
        try:
            parametros.PATHDLL = verifica_dll_firebird()
            parametros.DATABASEFB = caminho_bd()[0]
            inicializa_conexao_firebird()
            inicializa_conexao_mysql_replicador()

            connection_firebird = parametros.FIREBIRD_CONNECTION
            connection_mysql = parametros.MYSQL_CONNECTION_REPLICADOR
            
            try:
                firebird_mysql()
            finally:
                if not connection_firebird.closed:
                    connection_firebird.close()
                
                if connection_mysql.is_connected:
                    connection_mysql.close()
            print_log('Finalizado o envio de dados.', nome_servico)

        except Exception as e:
            print_log(f'Não foi possível executar serviço -> motivo: {e}', nome_servico)
        finally:
            remover_bloqueio(nome_servico)