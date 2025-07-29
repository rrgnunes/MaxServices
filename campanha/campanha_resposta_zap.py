import mysql.connector
import random
from funcoes.funcoes_zap import * 
from campanha_mensagens import mensagens
from funcoes.funcoes import inicializa_conexao_mysql, print_log

name_session = "00000000000000"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)

def responder_mensagens():
    name_session = "00000000000000"
    print_log(f"Procurando mensagens","campanha_resposta_zap")
    conexao_thread_receber = mysql.connector.connect(
        host=parametros.HOSTMYSQL,
        user=parametros.USERMYSQL,
        password=parametros.PASSMYSQL,
        database=parametros.BASEMYSQL,
        auth_plugin='mysql_native_password',  # Força o uso do plugin correto
        connection_timeout=15
    )         
      
    while True:
        try:
            mensagens_recebidas = receber_mensagem(name_session)

            for msg in mensagens_recebidas['response']:
                numero = msg['from'].split('@')[0][2:]    
                
                if parametros.MYSQL_CONNECTION is None:
                    inicializa_conexao_mysql()             
                if not parametros.MYSQL_CONNECTION.is_connected():
                    inicializa_conexao_mysql()                           
                           
                
                cur_con = conexao_thread_receber.cursor(dictionary=True)
                cur_con.execute(f'''select * from cliente_lead cl where campanha_enviado = 1 AND REPLACE(SUBSTRING_INDEX(cl.telefone, ' ', 2), ' ', '') = '{numero}'  ''')
                obj_empresas = cur_con.fetchall()
                
                if len(obj_empresas) == 0:
                    continue
                
                obj_empresas = obj_empresas[0]
                cur_con.close()                
                
                print_log(f"Recebido de {numero}","campanha_resposta_zap")

                mensagem_aleatoria = random.choice(mensagens)
                
                if obj_empresas:
                    envia_mensagem_zap(name_session, numero, mensagem_aleatoria)
                    print_log(f"Resposta enviada para {numero}","campanha_resposta_zap")
                    
                    cur_con = conexao_thread_receber.cursor(dictionary=True)
                    cur_con.execute(f'''UPDATE cliente_lead SET campanha_enviado = 2 WHERE codigo = {obj_empresas['codigo']} ''')
                    cur_con.close()
                    conexao_thread_receber.commit()                    
            
            time.sleep(5)  # Evita consultas excessivas
        except Exception as e:
            print_log(f"Erro na thread de resposta: {str(e)}","campanha_resposta_zap")
            conexao_thread_receber.rollback()
            time.sleep(5)  # Aguarda um pouco antes de tentar novamente
            
responder_mensagens()            