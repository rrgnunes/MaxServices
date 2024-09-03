import mysql.connector
import parametros

def generate_trigger_sql(cursor):
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM information_schema.tables 
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME != 'REPLICADOR'
    """)
    
    tables = cursor.fetchall()

    trigger_statements = []

    for (table_name,) in tables:
        cursor.execute(f"""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = '{table_name}'
              AND COLUMN_KEY = 'PRI'
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            pk_column = result[0]
            upper_table_name = table_name.upper()

            # SQL para o trigger de INSERT
            insert_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_INSERT AFTER INSERT ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE) VALUES ('{upper_table_name}', 'I', NEW.{pk_column});
                END IF;
            END;
            """
            trigger_statements.append(insert_trigger.strip())

            # SQL para o trigger de UPDATE
            update_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_UPDATE AFTER UPDATE ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE) VALUES ('{upper_table_name}', 'U', NEW.{pk_column});
                END IF;
            END;
            """
            trigger_statements.append(update_trigger.strip())

            # SQL para o trigger de DELETE
            delete_trigger = f"""
            CREATE TRIGGER TR_{upper_table_name}_DELETE AFTER DELETE ON {table_name} FOR EACH ROW
            BEGIN
                IF (SUBSTRING_INDEX(USER(), '@', 1) = 'maxsuport') THEN
                    INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE) VALUES ('{upper_table_name}', 'D', OLD.{pk_column});
                END IF;
            END;
            """
            trigger_statements.append(delete_trigger.strip())

    return trigger_statements

def get_tables_without_column(conn, banco:str,column:str) -> list:
    sql = """
        SELECT TABLE_NAME 
        FROM information_schema.tables 
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME != 'REPLICADOR'
    """

    cursor = conn.cursor()
    cursor.execute(sql)

    tables = cursor.fetchall()

    tables_without_colmun = []
    for (table,) in tables:
        try:
            sql_table = f"""SELECT COUNT(*) as "CAMPO" FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = {banco}
                            AND UPPER(TABLE_NAME) = UPPER('{table}') 
                            AND  UPPER(COLUMN_NAME) = UPPER('{column}')"""
            
            cursor.execute(sql_table)

            column_exists = cursor.fetchall()[0][0]
            if column_exists == 0:
                tables_without_colmun.append(table)
                
        except Exception as e:
            print(f'Nao foi possivel verificar coluna na tabela {table}: {e}')
       
    cursor.close()
    return tables_without_colmun

def add_column_to_tables(conn, column:str, column_type:str, tables:list[str], params:str='') -> list:
    erros = []
    cursor = conn.cursor()
    for table in tables:
        sql_alter = f"ALTER TABLE {table} ADD {column.upper()}"
        if column_type:
            sql_alter += f" {column_type.upper()}"
        if params:
            sql_alter += f" {params.upper()}"

        try:
            cursor.execute(sql_alter)
        except Exception as e:
            if cursor:
                cursor.close()
            erros.append(f'Não foi possivel executar comando ALTER na tabela {table}: {e}')
            
    cursor.close()
    return erros

# Conectar ao banco de dados MySQL
banco_mysql = '19775656000104'
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
        tables = get_tables_without_column(conn, banco_mysql, column)

        erros = add_column_to_tables(conn, column, column_type, tables)

        print(*erros)
    except Exception as e:
        if conn:
            conn.rollback()
    finally:
        conn.close()



# trigger(conn)

# column(conn)