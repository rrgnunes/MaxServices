from mysql.connector import connect


def mysql_connection(host, user, passwd, database=None):
    connection = connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database
    )
    return connection


HOSTMYSQL="177.153.69.3"
USERMYSQL="dinheiro"
PASSMYSQL="MT49T3.6%B"
BASEMYSQL="maxservices"

oConexao = mysql_connection(
    '177.153.69.3', 'dinheiro', 'MT49T3.6%B', 'maxservices')
