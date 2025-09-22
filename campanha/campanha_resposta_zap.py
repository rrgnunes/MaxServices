import mysql.connector
import random
import sys
import os

from campanha_mensagens import mensagens

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from funcoes.funcoes_zap import * 
from funcoes.funcoes import carregar_configuracoes, inicializa_conexao_mysql, print_log

name_session = "00000000000000"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)

def criar_conexao():
    return mysql.connector.connect(
        host=parametros.HOSTMYSQL,
        user=parametros.USERMYSQL,
        password=parametros.PASSMYSQL,
        database=parametros.BASEMYSQL,
        auth_plugin='mysql_native_password',
        connection_timeout=15
    )

def responder_mensagens():
    name_session = "00000000000000"
    print_log("Iniciando resposta única","campanha_resposta_zap")
    conexao = criar_conexao()

    try:
        if not conexao.is_connected():
            print_log("Falha na conexão MySQL","campanha_resposta_zap")
            return

        mensagens_recebidas = receber_mensagem(name_session)

        for msg in mensagens_recebidas.get('response', []):
            numero = msg['from'].split('@')[0][2:]

            if parametros.MYSQL_CONNECTION is None or not parametros.MYSQL_CONNECTION.is_connected():
                inicializa_conexao_mysql()

            cur_con = conexao.cursor(dictionary=True)
            cur_con.execute(f"""
                SELECT * 
                FROM cliente_lead cl 
                WHERE campanha_enviado = 1 
                AND REPLACE(SUBSTRING_INDEX(cl.telefone, ' ', 2), ' ', '') = '{numero}'
            """)
            obj_empresas = cur_con.fetchall()
            cur_con.close()

            if len(obj_empresas) == 0:
                continue

            obj_empresas = obj_empresas[0]
            print_log(f"Recebido de {numero}","campanha_resposta_zap")

            mensagem_aleatoria = random.choice(mensagens)
            envia_mensagem_zap(name_session, numero, mensagem_aleatoria)
            print_log(f"Resposta enviada para {numero}","campanha_resposta_zap")

            cur_con = conexao.cursor(dictionary=True)
            cur_con.execute(f"""
                UPDATE cliente_lead 
                SET campanha_enviado = 2 
                WHERE codigo = {obj_empresas['codigo']}
            """)
            cur_con.close()
            conexao.commit()

    except Exception as e:
        print_log(f"Erro: {str(e)}","campanha_resposta_zap")
        try:
            conexao.rollback()
        except:
            pass
    finally:
        conexao.close()

if __name__ == "__main__":
    responder_mensagens()