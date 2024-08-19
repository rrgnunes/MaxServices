import mysql.connector
from funcoes import inicializa_conexao_mysql, select,atualiza_mensagem,salva_retorno
from funcoes_zap import generate_token, start_session,envia_mensagem_zap
import parametros


def zapautomato():
    # Credenciais MySQL
    #parametros.HOSTMYSQL = "localhost"
    inicializa_conexao_mysql()
    resultado_zap = select('SELECT codigo, datahora, datahora_enviado, mensagem, fone, status, mensagem_padrao, cliente_id FROM zap_zap where status = "PENDENTE" ')

    for zap in resultado_zap:
        token_gerado = generate_token(zap['cliente_id'])
        parametros.TOKEN_ZAP = token_gerado['token']        
        conectado = start_session(zap['cliente_id'])
        if conectado:
            retorno_json = envia_mensagem_zap(zap['cliente_id'], zap['fone'], zap['mensagem'])

            if retorno_json['status'] == 'success':
                atualiza_mensagem(zap['codigo'], 'ENVIADA')   
                salva_retorno(zap['codigo'],retorno_json['status'])
            else:
                salva_retorno(zap['codigo'],retorno_json['message'])




zapautomato()