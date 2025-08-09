from mysql.connector import connect


def mysql_connection(host, user, passwd, database=None):
    connection = connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database
    )
    return connection


HOSTMYSQL="mysql.maxsuportsistemas.com"
USERMYSQL="maxservices"
PASSMYSQL="oC8qUsDp"
BASEMYSQL="maxservices"

oConexao = mysql_connection(HOSTMYSQL, USERMYSQL, PASSMYSQL, BASEMYSQL)
