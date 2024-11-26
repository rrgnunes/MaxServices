import fdb
import fdb.fbcore

def connect_firebird() -> fdb.Connection:
    try:
        conn = fdb.connect(host='localhost',
                        database='C:/MaxSuport_Rian/Dados/Dados.fdb',
                        user='maxsuport',
                        password='oC8qUsDp',
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
                    where rr.rdb$system_flag = 0 and rr.rdb$relation_name not in (upper('replicador'), upper('agenda'), 'V_AJUSTE_ESTOQUE','V_OS', 'V_PRODUTOS', 'V_VENDAS_NFCE')
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

if __name__ == '__main__':
    try:
        conn = connect_firebird()
        tables = get_tables(conn)
        # add_column_to_tables(conn, tables)
        conn.close()
    except Exception as er:
        print(f'Erro no processamento geral -> motivo: {er}')        
    finally:
        if not conn.closed:
            conn.close()