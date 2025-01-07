import fdb
import fdb.fbcore

def connect_firebird() -> fdb.Connection:
    try:
        conn = fdb.connect(host='localhost',
                        database='C:\\MaxSuport_Rian\\Dados\\Dados.fdb',
                        user='sysdba',
                        password='masterkey',
                        port=3050) 
        return conn
    except Exception as e:
        print(f'Não foi possível se conectar ao banco de dados -> motivo: {e}')

def get_tables(conn: fdb.Connection) -> list:
    try:

        if not conn.closed:
            sql = """select
                        trim(rr.rdb$relation_name)
                    from rdb$relations rr
                    where rr.rdb$system_flag = 0 and rr.rdb$relation_name not in (upper('replicador'), 'V_AJUSTE_ESTOQUE','V_OS', 'V_PRODUTOS', 'V_VENDAS_NFCE')
                    order by rr.rdb$relation_name"""
            cursor: fdb.fbcore.Cursor = conn.cursor()
            cursor.execute(sql)
            tables = cursor.fetchall()
            cursor.close()
            return tables
    except Exception as e:
        print(f'Não foi possivel pegar a lista de tabelas do banco de dados -> motivo: {e}')

def add_column_to_tables(conn: fdb.Connection, tables: list):
    try:

        if tables:
            cursor: fdb.fbcore.Cursor = conn.cursor()
            for (table,) in tables:
                try:
                    sql_alter = f'ALTER TABLE {table} ADD CODIGO_GLOBAL INTEGER;'
                    print(sql_alter)
                    cursor.execute(sql_alter)
                except Exception as er:
                    if 'attempt to store duplicate value (visible to active transactions) in unique index' in str(er).lower():
                        continue
                    else:
                        raise er
            conn.commit()
            cursor.close()
    except Exception as e:
        conn.rollback()
        print(f'Não foi possivel adcionar coluna as tabelas -> ult. tabela: {table} -> motivo: {e}')

def get_index_field(cur: fdb.fbcore.Cursor, table) -> str | None:
    try:
        sql = f"""SELECT
                    first 1
                    case
                        when (trim(i.rdb$field_name) = 'CODIGO') then 'CODIGO'
                        when (trim(i.rdb$field_name) = 'ID')     then 'ID'
                        when (trim(i.rdb$field_name) = 'CODIGO_PESSOA') then trim(i.rdb$field_name)
                        when (trim(rc.rdb$relation_name) in (i.rdb$field_name)) then trim(i.rdb$field_name)
                    end as campo
                FROM 
                    RDB$RELATION_CONSTRAINTS rc
                JOIN 
                    RDB$INDEX_SEGMENTS i ON rc.RDB$INDEX_NAME = i.RDB$INDEX_NAME
                WHERE 
                    rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
                AND
                    rc.rdb$relation_name = upper('{table}')
                ORDER BY 
                    rc.RDB$RELATION_NAME, i.RDB$FIELD_POSITION;"""
        cur.execute(sql)
        result = cur.fetchone()[0]
        return result
    except Exception as e:
        print(f'Não foi possível obter chave primaria da tabela: {table} - motivo: {e.__class__.__name__} -> {e}')

def get_field_type(cur: fdb.fbcore.Cursor, table: str, field: str) -> str:
    try:
        sql = f"""SELECT
                RF.RDB$RELATION_NAME as tabela, RF.RDB$FIELD_NAME as campo,
                CASE F.RDB$FIELD_TYPE
                    WHEN 7 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'SMALLINT'
                        WHEN 1 THEN 'NUMERIC(' || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 8 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'INTEGER'
                        WHEN 1 THEN 'NUMERIC('  || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 9 THEN 'QUAD'
                    WHEN 10 THEN 'FLOAT'
                    WHEN 12 THEN 'DATE'
                    WHEN 13 THEN 'TIME'
                    WHEN 14 THEN 'CHAR(' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ') '
                    WHEN 16 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'BIGINT'
                        WHEN 1 THEN 'NUMERIC'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 27 THEN 'DOUBLE'
                    WHEN 35 THEN 'TIMESTAMP'
                    WHEN 37 THEN 'VARCHAR'
                    WHEN 40 THEN 'CSTRING' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ')'
                    WHEN 45 THEN 'BLOB_ID'
                    WHEN 261 THEN 'BLOB SUB_TYPE ' || F.RDB$FIELD_SUB_TYPE
                    ELSE 'RDB$FIELD_TYPE: ' || F.RDB$FIELD_TYPE || '?'
                END as tipo
                FROM RDB$RELATION_FIELDS RF
                JOIN RDB$FIELDS F ON (F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE)
                LEFT OUTER JOIN RDB$CHARACTER_SETS CH ON (CH.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID)
                LEFT OUTER JOIN RDB$COLLATIONS DCO ON ((DCO.RDB$COLLATION_ID = F.RDB$COLLATION_ID) AND (DCO.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID))
                WHERE (COALESCE(RF.RDB$SYSTEM_FLAG, 0) = 0) AND RF.RDB$RELATION_NAME = UPPER('{table}') AND RF.RDB$FIELD_NAME = UPPER('{field}')
                ORDER BY RF.RDB$RELATION_NAME,RF.RDB$FIELD_NAME"""
        cur.execute(sql)
        result = cur.fetchall()[0][2]
        return result
    except Exception as e:
        print(f'Não foi possível obter tipo do campo : {field} da tabela: {table}, motivo: {e}')

def get_max_id(cur: fdb.fbcore.Cursor, table: str) -> int:
    try:
        index_field = get_index_field(cur, table)
        sql = f"SELECT MAX({index_field}) FROM {table}"
        cur.execute(sql)
        result = cur.fetchone()[0]
        if result == None:
            return 1
        return int(result)
    except Exception as e:
        print(f"Não foi possivel obter ultimo código da tabela: {table} motivo: {e}")

def create_generator(conn: fdb.Connection, table: str) -> str:
    try:
        cur = conn.cursor()
        biggest_id = get_max_id(cur, table)
        generator_name = f"GEN_{table}_ID"
        sql_create = f"CREATE SEQUENCE {generator_name};"
        sql_set = f"SET GENERATOR {generator_name} TO {biggest_id};"
        cur.execute(sql_create)
        cur.execute(sql_set)
        conn.commit()
        return generator_name
    except Exception as e:
        conn.rollback()
        if f'Generator {generator_name} already exists' in str(e):
            return generator_name
        print(f'Não foi possível criar generetor para tabela: {table} motivo: {e}')
    finally:
        if cur:
            cur.close()

def add_triggers(conn: fdb.Connection, tables: list):
    cur = conn.cursor()
    try:
        for (table, ) in tables:

            index_field = get_index_field(cur, table)
            if index_field == None:
                continue

            index_type = get_field_type(cur, table, index_field)
            if index_type not in ('INTEGER', 'SMALLINT'):
                continue
            try:
                generator_name = create_generator(conn, table)
                if not generator_name:
                    raise
                sql_trigger = f"""CREATE OR ALTER TRIGGER TR_{table}_BI FOR {table}
                                ACTIVE BEFORE INSERT POSITION 0
                                AS
                                BEGIN
                                    IF (NEW.{index_field} IS NULL) THEN
                                        NEW.{index_field} = GEN_ID({generator_name}, 1);
                                    ELSE
                                        BEGIN
                                            EXECUTE STATEMENT 'SET GENERATOR {generator_name} TO ' || NEW.{index_field};
                                        END
                                END"""
            except Exception:
                print('Erro ocorrido, continuando...')
                continue
            print(f'Criando trigger:\n{sql_trigger}')
            cur.execute(sql_trigger)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Não foi possivel criar trigger {sql_trigger} \n motivo: {e}')

if __name__ == '__main__':
    try:
        conn = connect_firebird()
        tables = get_tables(conn)
        # add_column_to_tables(conn, tables)
        add_triggers(conn, tables)
        conn.close()
    except Exception as er:
        print(f'Erro no processamento geral -> motivo: {er}')        
    finally:
        if not conn.closed:
            conn.close()