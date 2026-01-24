import os
import sys
from datetime import datetime, timedelta
from fdb import Cursor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from funcoes.funcoes import (
    updatefb,
    print_log,
    obter_dados_ini,
    pode_executar,
    criar_bloqueio,
    remover_bloqueio,
    verifica_dll_firebird,
    carrega_arquivo_config,
    fechar_conexao_firebird,
    inicializa_conexao_firebird
    )


def marcar_logado(codigo_empresa, codigo_usuario):
    print_log(f"Marcando usuario {codigo_usuario} da empresa {codigo_empresa} como logado.", nome_script)
    sql = "UPDATE USUARIOS SET LOGADO = 1 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

def marcar_deslogado(codigo_empresa, codigo_usuario):
    print_log(f"Marcando usuario {codigo_usuario} da empresa {codigo_empresa} como deslogado.", nome_script)
    sql = "UPDATE USUARIOS SET LOGADO = 0 WHERE FK_EMPRESA = ? AND CODIGO = ?"
    updatefb(sql, (codigo_empresa, codigo_usuario))

def verifica_usuarios():

    carrega_arquivo_config()

    for cnpj, dados_cnpj in params.CNPJ_CONFIG['sistema'].items():

        caminho_sistema = params.SCRIPT_PATH.lower().replace('server', '')
        if not dados_cnpj['caminho_base_dados'] or dados_cnpj['caminho_base_dados'] == 'None':
            continue


        caminho_sistema = dados_cnpj.get('caminho_base_dados', '').lower().replace('\\dados.fdb', '').replace('dados', '')
        caminho_banco_ini = os.path.join(caminho_sistema, 'banco.ini')
        dados_ini = obter_dados_ini(caminho_banco_ini)

        print_log(f"Verificando usuarios da pasta: {caminho_sistema}", nome_script)
        params.PATHDLL = verifica_dll_firebird()
        params.DATABASEFB = dados_ini['caminho_banco']

        inicializa_conexao_firebird()

        sql_select = f"SELECT CODIGO, FK_EMPRESA, LOGADO, ULT_EXEC_USUARIO FROM USUARIOS WHERE ATIVO = 'S'"
        cursor = None
        try:
            print_log(f"Consultando usuarios do sistema...", nome_script)
            cursor: Cursor = params.FIREBIRD_CONNECTION.cursor()
            cursor.execute(sql_select)
            usuarios = cursor.fetchall()
            hora_atual = datetime.now()

            for usuario in usuarios:
                
                if usuario[2] == 0:
                    continue
                
                if not usuario[3]:
                    marcar_deslogado(usuario[1], usuario[0])
                    continue

                if (hora_atual - usuario[3]) > timedelta(seconds=20):
                    marcar_deslogado(usuario[1], usuario[0])

        except Exception as e:
            print_log(f"Não foi possível verificar usuarios -> motivo: {e}")
            
        finally:
            print_log("Consulta de usuarios finalizada.", nome_script)
            if cursor:
                cursor.close()
            fechar_conexao_firebird()


if __name__ == "__main__":

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            verifica_usuarios()
        except Exception as e:
            print_log(f"Erro ao tentar iniciar verificação -> motivo: {e}", nome_script)
        finally:
            remover_bloqueio(nome_script)