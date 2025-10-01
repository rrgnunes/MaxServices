import os
import sys
import time
import mysql.connector
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes_zap import generate_token, start_session,envia_mensagem_zap
from funcoes.funcoes import inicializa_conexao_mysql, select,atualiza_mensagem,salva_retorno,print_log, pode_executar, criar_bloqueio, remover_bloqueio

def zapautomato():
    # Definir as credenciais do MySQL
    parametros.HOSTMYSQL = "177.153.69.3"
    
    # Inicializa a conexão com o banco de dados MySQL
    inicializa_conexao_mysql()
    print_log("Conexão com MySQL inicializada.")
    
    # Seleciona mensagens pendentes de envio no banco de dados
    resultado_zap = select('SELECT codigo, datahora, datahora_enviado, mensagem, fone, status, cliente_id FROM zap_zap where status = "PENDENTE" order by cliente_id')
    print_log(f"Mensagens pendentes obtidas: {len(resultado_zap)} mensagens.")
 
    # Gera um token para o cliente
    token_gerado = generate_token(resultado_zap[0]['cliente_id'])
    parametros.TOKEN_ZAP = token_gerado['token']
    ultimo_cnpj = ''

    for zap in resultado_zap:
        if zap['cliente_id'] != ultimo_cnpj:
            token_gerado = generate_token(resultado_zap[0]['cliente_id'])  
            parametros.TOKEN_ZAP = token_gerado['token']

        print_log(f"Token gerado para o cliente {zap['cliente_id']}: {parametros.TOKEN_ZAP}")
        
        # Inicia a sessão de envio de mensagens
        conectado = start_session(zap['cliente_id'])
        print_log(f"Sessão iniciada para o cliente {zap['cliente_id']}: {'conectado' if conectado else 'não conectado'}")
        
        if conectado:
            # Envia a mensagem via WhatsApp
            retorno_json = envia_mensagem_zap(zap['cliente_id'], zap['fone'], zap['mensagem'])
            print_log(f"Mensagem enviada para {zap['fone']}: {retorno_json}")
            
            if retorno_json['status'] == 'success':
                # Atualiza o status da mensagem para 'ENVIADA' no banco de dados
                atualiza_mensagem(zap['codigo'], 'ENVIADA')
                print_log(f"Status da mensagem {zap['codigo']} atualizado para 'ENVIADA'.")
                
                # Salva o status de retorno do envio
                salva_retorno(zap['codigo'], retorno_json['status'])
                print_log(f"Retorno salvo para a mensagem {zap['codigo']}: {retorno_json['status']}")
            else:
                # Salva a mensagem de erro de retorno do envio
                salva_retorno(zap['codigo'], retorno_json['message'])
                print_log(f"Erro ao enviar mensagem {zap['codigo']}: {retorno_json['message']}")
        ultimo_cnpj = zap['cliente_id']
        
        segundos = random.randint(10, 60)  # tempo aleatório entre 1 e 10 segundos
        time.sleep(segundos)


if __name__ == '__main__':
    # Pega o nome do arquivo
    script_name = os.path.basename(sys.argv[0]).replace('.py', '')  

    # verifica se pode ser executado
    if pode_executar(script_name):
        # cria o arquivo de bloqueio com a data e hora em que foi iniciado
        criar_bloqueio(script_name)
        try:
            zapautomato()
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar: {e}')
        finally:
            # ao finalizar a execução remove o arquivo de bloqueio
            remover_bloqueio(script_name)