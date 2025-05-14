from funcoes_pdv import fechar_venda_mesa, cancelar_fechar_venda_mesa
import parametros
from funcoes import get_local_ip, carregar_configuracoes

host = get_local_ip()  # Obtém o IP local da máquina
if host == '192.168.10.115':
    parametros.HOSTFB = '192.168.10.242'

carregar_configuracoes()

codigo_venda = fechar_venda_mesa(3, 1)



cancelar_fechar_venda_mesa(codigo_venda)


