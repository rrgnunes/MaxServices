import parametros
import os
import sys
from funcoes import (
    inicializa_conexao_mysql_replicador,
    inicializa_conexao_firebird,print_log,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    caminho_bd,
    verifica_dll_firebird,
    consulta_cnpjs_local,
    buscar_nome_chave_primaria,
    tratar_valores,
    verifica_valor_chave_primaria,
    buscar_elemento_mysql,
    buscar_elemento_firebird,
    delete_registro_replicador
    )


def buscar_alteracoes_replicador_mysql(empresas: list) -> list:
    """
    Função responsavel por buscar as alterações feitas no banco de dados remoto, considerando a tabela replicador,
    e filtrando somente os dados pertencentes aos cnpjs passados para a função
    """
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

def update_firebird(tabela: str, codigo: int, dados: dict,  codigo_global: int = 0) -> None:
    """
    Atualiza o registro no banco local na tabela informada de acordo com o registro do banco remoto
    """
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
    """
    Insere o registro no banco local de acordo com o registro criado no banco remoto
    """
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
    """
    Deleta o registro local de acordo com o registro remoto deletado
    """
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


def mysql_firebird():
    """
    Loop principal sobre os registros capturados do banco remoto
    """

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
                mysql_firebird()
            finally:
                if not connection_firebird.closed:
                    connection_firebird.close()
                
                if connection_mysql.is_connected:
                    connection_mysql.close()

            print_log('Finalizado o retorno de dados.')
        except Exception as e:
            print_log(f'Não foi possível executar serviço -> motivo: {e}', nome_servico)
        finally:
            remover_bloqueio(nome_servico)