from conexao import oConexao


def insert_IBPT(valores):
    query = ("""INSERT INTO ibpt_ibpt
        (codigo, ex, tipo, descricao, nacional_federal, importados_federal,
         estadual, municipal, vigencia_inicio, vigencia_fim, chave, versao,
         fonte, estado)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

    # valida: lista/tupla de tuplas e sem tipos compostos
    assert isinstance(valores, (list, tuple)) and all(isinstance(r, tuple) for r in valores)
    for r in valores:
        if any(isinstance(c, (tuple, list, dict)) for c in r):
            raise TypeError("Campo composto dentro da tupla de valores.")

    if not oConexao.is_connected():
        oConexao.connect()

    cur = oConexao.cursor(buffered=True)
    try:
        cur.executemany(query, valores)
        oConexao.commit()
    finally:
        cur.close()


def delete_IBPT_versao_diferente(estado, versao):
    query = "DELETE FROM ibpt_ibpt WHERE estado = '" + \
        estado + "' AND versao <> '"+versao+"'"
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor(buffered=True)
    oCursor.execute(query)
    oConexao.commit()


def select_IBPT(codigo=None, estado=None):
    query = "SELECT * FROM ibpt_ibpt "
    delim = " WHERE "
    if codigo != None:
        query += delim + " codigo = '" + codigo + "'"
        delim = ' AND '

    if estado != None:
        query += delim + " estado = '" + estado + "'"
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor()
    oCursor.execute(query)
    return oCursor


def select_versao_IBPT(versao=None, estado=None):
    query = "SELECT * FROM ibpt_ibpt "
    delim = " WHERE "
    if versao != None:
        query += delim + " versao = '" + versao + "'"
        delim = ' AND '

    if estado != None:
        query += delim + " estado = '" + estado + "'"
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor()
    oCursor.execute(query)
    return oCursor.fetchall()


def select_distinct_IBPT(estado=None):
    query = "SELECT DISTINCT codigo FROM ibpt_ibpt WHERE estado = '" + estado + "'"
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor()
    oCursor.execute(query)
    return oCursor.fetchall()
