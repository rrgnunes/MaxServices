import mysql.connector

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


# Conectar ao banco de dados MySQL
conn = mysql.connector.connect(
    host='177.153.69.3',
    user='maxservices',#maxsuport
    password='oC8qUsDp',
    database='19775656000104'
)

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
