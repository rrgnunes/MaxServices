# from funcoes import *

# parametros.BANCO_SQLITE = 'c:\\maxsuport\\dados\\dados.db'
# retorno_atualizacao = check_banco_atualizar()
# a = ''

# from thread_atualiza_banco import *

# a = threadatualizabanco()
# a.start()

from thread_api_maxsuport import *

a = threadapimaxsuport()
a.start()
a.join()