# from funcoes import *

# parametros.BANCO_SQLITE = 'c:\\maxsuport\\dados\\dados.db'
# retorno_atualizacao = check_banco_atualizar()
# a = ''

# from thread_atualiza_banco import *

# a = threadatualizabanco()
# a.start()

from thread_backup_local import *

a = threadbackuplocal()
a.start()
a.join()