from funcoes_zap import * 

name_session = "19775656000104"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)
if retorno['status'] != 'CONNECTED':
    gera_qrcode(str(retorno['qrcode']).split(',')[1])
status_session(name_session)
envia_mensagem_zap(name_session,'6699710593','teste')
name_session = name_session