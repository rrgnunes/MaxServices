import fdb.fbcore
import mysql.connector
import mysql.connector.cursor
import parametros
import fdb

def connection_aux() -> fdb.Connection:
    fdb.load_api('C:/Program Files/Firebird/firebird_2_5/bin/fbclient.dll')
    conn = fdb.connect(host='localhost',
                       database='C:/MaxSuport_Rian/Dados/Dados.fdb',
                       user='SYSDBA',
                       password='masterkey',
                       port=3050)
    return conn


def generate_trigger_sql(cursor):
    conn = connection_aux()
    cursor_aux:fdb.fbcore.Cursor = conn.cursor()
    tables = get_tables(cursor)

    trigger_statements = []

    for (table_name,) in tables:
        # cursor.execute(f"""
        #     SELECT COLUMN_NAME 
        #     FROM information_schema.COLUMNS
        #     WHERE TABLE_SCHEMA = DATABASE() 
        #       AND TABLE_NAME = '{table_name}'
        #       AND COLUMN_KEY = 'PRI'
        #     LIMIT 1
        # """)
        cursor_aux.execute(f"""SELECT
                        first 1 
                        trim(i.RDB$FIELD_NAME) AS COLUNA
                    FROM 
                        RDB$RELATION_CONSTRAINTS rc
                    JOIN 
                        RDB$INDEX_SEGMENTS i ON rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
                    WHERE 
                        rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
                    AND
                        rc.rdb$relation_name = upper('{table_name}')
                    ORDER BY 
                        rc.RDB$RELATION_NAME, i.RDB$FIELD_POSITION;""")
        result = cursor_aux.fetchone()
        
        if result:
            pk_column = result[0]
            upper_table_name = table_name.upper()

            # SQL para o trigger de INSERT
            insert_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_INSERT AFTER INSERT ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE, CNPJ_EMPRESA, CODIGO_GLOBAL) VALUES ('{upper_table_name}', 'I', NEW.{pk_column}, NEW.CNPJ_EMPRESA, NEW.CODIGO_GLOBAL);
                END IF;
            END;
            """
            trigger_statements.append(insert_trigger.strip())

            # SQL para o trigger de UPDATE
            update_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_UPDATE AFTER UPDATE ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE, CNPJ_EMPRESA, CODIGO_GLOBAL) VALUES ('{upper_table_name}', 'U', NEW.{pk_column}, NEW.CNPJ_EMPRESA, NEW.CODIGO_GLOBAL);
                END IF;
            END;
            """
            trigger_statements.append(update_trigger.strip())

            # SQL para o trigger de DELETE
            delete_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_DELETE AFTER DELETE ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE, CNPJ_EMPRESA, CODIGO_GLOBAL) VALUES ('{upper_table_name}', 'D', OLD.{pk_column}, OLD.CNPJ_EMPRESA, OLD.CODIGO_GLOBAL);
                END IF;
            END;
            """
            trigger_statements.append(delete_trigger.strip())

    return trigger_statements

def get_tables(cur) -> list[tuple]:
    sql = """
        SELECT TABLE_NAME 
        FROM information_schema.tables 
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME NOT IN ('REPLICADOR', 'auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 
        'auth_user_user_permissions', 'django_admin_log', 'django_content_type', 'django_migrations', 'django_session')
    """
    try:
        cur.execute(sql)
        tables = cur.fetchall()
        return tables
    except Exception as e:
        print(f'Não foi possível pegar as tabelas do sistema: {e}')
        return

def drop_triggers(conn: mysql.connector.MySQLConnection):

    try:
        cur = conn.cursor()
        tables = get_tables(cur)
        triggers_names = []
        for (table,) in tables:
            triggers_names.append(f'TR_{table.upper()}_INSERT')
            triggers_names.append(f'TR_{table.upper()}_UPDATE')
            triggers_names.append(f'TR_{table.upper()}_DELETE')

        for trigger_name in triggers_names:
            try:
                sql_drop = f'DROP TRIGGER {trigger_name}'
                cur.execute(sql_drop)
                print(sql_drop)
            except Exception as err:
                if 'trigger does not exist' in str(err).lower():
                    print(f'Trigger não existe!!!: {trigger_name}')
                    continue
                else:
                    raise err

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)


def remove_foreign_key(conn: mysql.connector.MySQLConnection):

    sql = """SELECT
                rc.TABLE_NAME,
                rc.CONSTRAINT_NAME
             FROM information_schema.`REFERENTIAL_CONSTRAINTS` rc
             where rc.TABLE_NAME not in ('auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 
                    'auth_user_user_permissions', 'django_admin_log', 'django_content_type', 'django_migrations', 'django_session')"""
    
    try:

        cur = conn.cursor()
        cur.execute(sql)
        tables_and_fks = cur.fetchall()

        for table, fk in tables_and_fks:
            sql_drop = f'ALTER TABLE {table} DROP FOREIGN KEY `{fk}`'
            print(sql_drop)
            cur.execute(sql_drop)
        conn.commit()
        print('Chaves Estrangeiras removidas com sucesso!')
    except Exception as e:
        print(e)

def remove_primary_key(conn: mysql.connector.MySQLConnection):
    cur = conn.cursor()
    try:
        tables = get_tables(cur)
        for (table, ) in tables:
            try:
                sql_drop = f'ALTER TABLE {table.upper()} DROP PRIMARY KEY;'
                print(sql_drop)
                cur.execute(sql_drop)
            except Exception as e:
                if 'incorrect table definition; there can be only one auto column and it must be defined as a key' in str(e).lower():
                    print('Tabela não possui chave primaria!')
                    continue
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Não foi possivel apagar as chaves primarias: {e}')


def get_tables_without_column(conn, banco:str,column:str) -> list:
    cursor = conn.cursor()

    tables = get_tables(cursor)

    tables_without_colmun = []
    for (table,) in tables:
        try:
            sql_table = f"""SELECT COUNT(*) as "CAMPO" FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = '{banco}'
                            AND UPPER(TABLE_NAME) = UPPER('{table}') 
                            AND  UPPER(COLUMN_NAME) = UPPER('{column}')"""
            
            cursor.execute(sql_table)
            print(f'Lendo tabela {table}')
            column_exists = cursor.fetchall()[0][0]
            if column_exists == 0:
                tables_without_colmun.append(table)
                
        except Exception as e:
            print(f'Nao foi possivel verificar coluna na tabela {table}: {e}')
       
    cursor.close()
    return tables_without_colmun

def create_indice(conn: mysql.connector.MySQLConnection):
    cur = conn.cursor()
    tables = get_tables(cur)
    try:
        tables_with_column = []
        for (table, ) in tables:
            sql_table = f"""SELECT COUNT(*) as "CAMPO" FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_SCHEMA = 'dados'
                                AND UPPER(TABLE_NAME) = UPPER('{table}') 
                                AND UPPER(COLUMN_NAME) = UPPER('CNPJ_EMPRESA')"""
            cur.execute(sql_table)
            print(f'Lendo tabela {table}')
            column_exists = cur.fetchall()[0][0]
            if column_exists > 0:
                tables_with_column.append(table)

        for table_with_column in tables_with_column:
            sql_alter = f'ALTER TABLE {table_with_column} ADD INDEX IDX_CNPJ_EMPRESA_{table_with_column} (CNPJ_EMPRESA);'
            print(sql_alter)
            cur.execute(sql_alter)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        if cur:
            cur.close()

def remove_not_null(conn: mysql.connector.MySQLConnection):
    cur = conn.cursor()
    tables = get_tables(cur)
    try:
        tables_with_column = []
        for (table, ) in tables:
            sql_table = f"""SELECT COUNT(*) as "CAMPO" FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_SCHEMA = 'dados'
                                AND UPPER(TABLE_NAME) = UPPER('{table}') 
                                AND UPPER(COLUMN_NAME) = UPPER('CODIGO')"""
            cur.execute(sql_table)
            print(f'Lendo tabela {table}')
            column_exists = cur.fetchall()[0][0]
            if column_exists > 0:
                tables_with_column.append(table)

        for table_with_column in tables_with_column:
            sql_alter = f'ALTER TABLE {table_with_column} MODIFY CODIGO INTEGER NULL;'
            print(sql_alter)
            cur.execute(sql_alter)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Erro ao remover null: {e}')
    finally:
        if cur:
            cur.close()

def add_column_to_tables(conn: mysql.connector.MySQLConnection, column:str, column_type:str, tables:list[str], params:str='') -> list:
    erros = []
    cursor = conn.cursor()
    for table in tables:
        sql_alter = f"ALTER TABLE {table} ADD {column.upper()}"
        if column_type:
            sql_alter += f" {column_type.upper()}"
        if params:
            sql_alter += f" {params.upper()}"

        try:
            print(sql_alter)
            cursor.execute(sql_alter)
        except Exception as e:
            if cursor:
                cursor.close()
            erros.append(f'Não foi possivel executar comando ALTER na tabela {table}: {e}')
            
    cursor.close()
    return erros

# Conectar ao banco de dados MySQL
banco_mysql = 'dados'
conn = mysql.connector.connect(
    host=parametros.HOSTMYSQL,
    user=parametros.USERMYSQL,
    password=parametros.PASSMYSQL,
    database=banco_mysql
)

def trigger(conn):
    cursor = conn.cursor()

    # Gerar o SQL para os triggers
    trigger_sql = generate_trigger_sql(cursor)

    # Executar cada script SQL no banco de dados
    for sql in trigger_sql:
        try:
            cursor.execute(sql)
            print(f"Trigger criado com sucesso:\n{sql}\n")
        except mysql.connector.Error as err:
            print(f"Erro ao criar o trigger:\n{sql}\nErro: {err}\n")

    # Confirmar as mudanças
    conn.commit()

    cursor.close()
    conn.close()

def column(conn):
    try:
        column = 'CNPJ_EMPRESA'
        column_type = 'varchar(20)'
        params = ''
        tables = get_tables_without_column(conn, banco_mysql, column)

        erros = add_column_to_tables(conn, column, column_type, tables, params)

        print(*erros)
    except Exception as e:
        if conn:
            conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    print('Iniciando')
    trigger(conn)

    # column(conn)

    # drop_triggers(conn)

    # remove_primary_key(conn)

    # create_indice(conn)

    # remove_not_null(conn)