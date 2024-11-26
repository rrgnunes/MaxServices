import mysql.connector
from funcoes import inicializa_conexao_mysql, select,atualiza_mensagem,salva_retorno,print_log
from funcoes_zap import generate_token, start_session,envia_mensagem_zap
import parametros
import os
import sys
import time

def zapautomato():
    # Definir as credenciais do MySQL
    parametros.HOSTMYSQL = "localhost"
    
    # Inicializa a conexão com o banco de dados MySQL
    inicializa_conexao_mysql()
    print_log("Conexão com MySQL inicializada.")
    
    # Seleciona mensagens pendentes de envio no banco de dados
    resultado_zap = select('SELECT codigo, datahora, datahora_enviado, mensagem, fone, status, cliente_id FROM zap_zap where status = "PENDENTE"')
    print_log(f"Mensagens pendentes obtidas: {len(resultado_zap)} mensagens.")
 
    # Gera um token para o cliente
    token_gerado = generate_token(resultado_zap[0]['cliente_id'])
    parametros.TOKEN_ZAP = token_gerado['token']

    for zap in resultado_zap:
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

        time.sleep(10)

# Executa a função principal para automatizar o envio de mensagens
# Nome do arquivo de bloqueio
LOCK_FILE = '/tmp/zap_automato.lock'

# Verificar se o arquivo de bloqueio existe
if os.path.exists(LOCK_FILE):
    print_log("O script já está em execução.")
    sys.exit()

# Criar o arquivo de bloqueio
open(LOCK_FILE, 'w').close()

try:
    # Executa a função principal para automatizar o envio de mensagens
    zapautomato()
finally:
    # Remover o arquivo de bloqueio ao final da execução
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)