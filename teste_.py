import parametros
import os
from funcoes import comparar_metadados, buscar_estrutura_remota
from salva_metadados_json import salva_json_metadados_local


# salva_json_metadados_local(r'C:\MaxSuport\Dados\Dados.fdb')
# buscar_estrutura_remota()
metadados_origem = os.path.join(parametros.SCRIPT_PATH, 'metadados_remoto')
metadados_local = os.path.join(parametros.SCRIPT_PATH, 'metadados_local')

comparar_metadados(metadados_origem, metadados_local)