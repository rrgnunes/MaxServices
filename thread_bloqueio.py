from logging.handlers import RotatingFileHandler
import fdb
import psutil

import parametros
from funcoes import print_log, exibe_alerta, inicializa_conexao_mysql, carregar_configuracoes

def verifica_dados_local():
    try:
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
                    comando = 'Liberar' if ativo == "1" else 'Bloquear'
                    print_log(f"Comando para {comando} maxsuport","thread_bloqueio")
                    cur.execute(f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}'")
                    con.commit()
                except fdb.fbcore.DatabaseError as e:
                    print_log(f"Erro ao executar consulta: {e}")
    
    except Exception as e:
        print_log(f"Erro: {e}","thread_bloqueio")

verifica_dados_local()