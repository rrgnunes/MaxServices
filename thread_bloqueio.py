from logging.handlers import RotatingFileHandler
import fdb
import psutil
import os
import pathlib
import parametros
from funcoes import print_log, exibe_alerta, inicializa_conexao_mysql, carregar_configuracoes

def verifica_dados_local():
    try:
        lock_bloqueio = os.path.join(pathlib.Path(__file__).parent, 'lock_bloqueio.txt')
        if os.path.exists(lock_bloqueio):
            print_log('Em execucao', "thread_bloqueio")
            return
        else:
            with open(lock_bloqueio, 'w') as arq:
                arq.write('em execucao')
        inicializa_conexao_mysql()
        carregar_configuracoes()        
        print_log("Pegando dados locais","thread_bloqueio")
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():
            ativo = dados_cnpj['sistema_ativo']
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil'].replace('\\', '/')
            caminho_base_dados_gfil = caminho_base_dados_gfil.split('/')[0] + '/' + caminho_base_dados_gfil.split('/')[1]

            print_log(f"Local valor {ativo} do CNPJ {cnpj}","thread_bloqueio")

            if ativo == "0" and sistema_em_uso == "2":
                print_log("Encerra Processo do GFIL","thread_bloqueio")
                for proc in psutil.process_iter(['name', 'exe']):
                    if 'FIL' in proc.info['name']:
                        if caminho_base_dados_gfil in proc.info['exe'].replace('\\', '/'):
                            print_log(f"Encerra Processo do GFIL na proc {caminho_base_dados_gfil}, no caminho {proc.info['exe']}","thread_bloqueio")
                            proc.kill()
                            print_log("Iniciar conexão com alerta","thread_bloqueio")
                            exibe_alerta()

            if sistema_em_uso == "1":
                data_cripto = '80E854C4A6929988F97AE2'
                if ativo == "1":
                    data_cripto = '80E854C4A6929988F879E1'
                try:
                    con = parametros.FIREBIRD_CONNECTION
                    cur = con.cursor()
                    cur.execute(f"select DATA_VALIDADE from empresa where cnpj = {cnpj} and DATA_VALIDADE = '80E854C4A6929988F879E1' ") # se houver retorno é porque esta ativo
                    sistema_ativo = len(cur.fetchall()) > 0
                    if sistema_ativo != (ativo == '1'):
                        comando = 'Liberar' if ativo == "1" else 'Bloquear'
                        print_log(f"Comando para {comando} maxsuport","thread_bloqueio")
                        cur.execute(f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}'")
                    con.commit()
                except fdb.fbcore.DatabaseError as e:
                    print_log(f"Erro ao executar consulta: {e}")
        os.remove(lock_bloqueio)
    except Exception as e:
        print_log(f"Erro: {e}","thread_bloqueio")
        os.remove(lock_bloqueio)

verifica_dados_local()