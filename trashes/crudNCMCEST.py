from conexao import oConexao


def insert_NCMCEST(valores):
    consulta = select_NCMCEST(valores[0][0], valores[0][1])
    if len(consulta) > 0:
        return
    query = """INSERT INTO ibpt_ncmcest (ncm, cest) VALUES (%s,%s)"""
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor(buffered=True)
    oCursor.executemany(query, valores)
    oConexao.commit()


def select_NCMCEST(NCM=None, CEST=None):
    query = "SELECT * FROM ibpt_ncmcest "
    delim = " WHERE "
    if NCM != None:
        query += delim + " ncm = " + NCM
        delim = ' AND '

    if CEST != None:
        query += delim + " cest = " + CEST
    if not oConexao.is_connected:
        oConexao.connect()
    oCursor = oConexao.cursor()
    oCursor.execute(query)
    return oCursor.fetchall()
