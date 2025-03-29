from funcoes import carregar_configuracoes, inicializa_conexao_mysql, print_log, envia_audio_texto_api_comando
import threading
from funcoes_zap import * 
import mysql.connector
import random
from campanha_mensagens import mensagens

name_session = "00000000000001"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)

def formatar_relatorio_whatsapp(dados):
    if not dados:
        return "📌 *Relatório vazio.* Nenhum dado encontrado."

    mensagem = "📌 *Relatório de Resultados* 📌\n\n"

    for item in dados:
        for chave, valor in item.items():
            mensagem += f"*{chave.replace('_', ' ').title()}:* {valor}\n"
        mensagem += "--------------------------------\n"

    return mensagem

def responder_mensagens():
    while True:
        try:
            print_log(f"Procurando mensagens")
            conexao_maxservices_mensagem = mysql.connector.connect(
                host=parametros.HOSTMYSQL,
                user=parametros.USERMYSQL,
                password=parametros.PASSMYSQL,
                database=parametros.BASEMYSQL,
                #auth_plugin='mysql_native_password',  # Força o uso do plugin correto
                connection_timeout=15
            )                   
            mensagens_recebidas = receber_mensagem(name_session)

            for msg in mensagens_recebidas['response']:
                numero = msg['from'].split('@')[0][2:]    
                
                if numero not in ('6697145422','6692825191'):
                    envia_mensagem_zap(name_session, numero, 'Este número não esta habilitado para serviços MaxSuport')
                    continue                      
                
                envia_mensagem_zap(name_session, numero, 'Vou processar esses dados... Aguarde por favor')        
                
                cur_con = conexao_maxservices_mensagem.cursor(dictionary=True)
                cur_con.execute(f'''select cnpj from cliente_cliente cl where cnpj = '19775656000104'  ''')
                obj_empresas = cur_con.fetchall()
                
                if len(obj_empresas) == 0:
                    continue
                
                obj_empresas = obj_empresas[0]
                cur_con.close()                
                
                if msg['type'] == 'chat':  
                    texto = msg['body']
                    resposta = envia_audio_texto_api_comando('texto', texto, obj_empresas['cnpj'])
                else:
                    arquivo_audio = baixar_audio(name_session, msg['id'])
                    resposta = envia_audio_texto_api_comando('audio', arquivo_audio, obj_empresas['cnpj'])                
                    
                # Converte a string JSON em dicionário
                dados = json.loads(resposta)

                # Pega apenas o campo "resultado"
                resposta = dados.get("resultado")
                
                resposta = formatar_relatorio_whatsapp(resposta)
                
                envia_mensagem_zap(name_session, numero, resposta)         
            
            conexao_maxservices_mensagem.close()
            conexao_maxservices_mensagem = None
            print_log(f"Descansando")
            time.sleep(5)  # Evita consultas excessivas

        except Exception as e:
            print_log(f"Erro na thread de resposta: {str(e)}")
            conexao_maxservices_mensagem.rollback()
            time.sleep(5)  # Aguarda um pouco antes de tentar novamente
            
responder_mensagens()            