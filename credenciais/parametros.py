# parametros.py
import os
import fdb
import mysql
import mysql.connector

# Credenciais MySQL
#Contabo
HOSTMYSQL = "maxsuportsistemas.com"

#Kinghost
# HOSTMYSQL = "177.153.69.3"
USERMYSQL = "maxservices"
PASSMYSQL = "oC8qUsDp"
BASEMYSQL = "maxservices"

# Replicador
HOSTMYSQL_REP = "maxsuportsistemas.com"
BASEMYSQL_REP = "dados"


# Credenciais Firebird
USERFB = 'maxservices'
PASSFB = 'oC8qUsDp'
HOSTFB = 'localhost'
DATABASEFB = ''  # Atualizar conforme necessário
PORTFB = 3050  # Atualizar conforme necessário
PATHDLL = ''  # Atualizar conforme necessário

# Credenciais Dropbox
APP_KEY_DROP_BOX = ''
APP_SECRET_DROP_BOX = ''
ACCESS_TOKEN_DROP_BOX = ''
REFRESH_TOKEN_DROP_BOX = ''
CODIGO_ACESSO_DROP_BOX = ''

# Outras configurações
SERVIDOR = False
BANCO_SQLITE = ''
PASTA_MAXSUPORT = ''

# Configurações do Zap
TOKEN_ZAP = ''
LAST_IMAGE = ''

# Conexões globais (inicialmente None)
MYSQL_CONNECTION: mysql.connector.MySQLConnection = None
MYSQL_CONNECTION_REPLICADOR: mysql.connector.MySQLConnection = None
FIREBIRD_CONNECTION: fdb.Connection  = None


# Variáveis globais
CNPJ_CONFIG = {}
ATIVO = ''

# Caminho do script atual
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('credenciais', '')

# Scantech
USUARIOSCANTECH = ''
SENHASCANTECH = ''
IDEMPRESASCANTECH = 0
IDLOCALSCANTECH = 0
URLBASESCANTECH = ''


