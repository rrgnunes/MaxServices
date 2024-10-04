import fdb
import parametros
import os
import pathlib
import datetime as dt
from funcoes import (
    os,json,datetime,atualiza_agenda, retorna_pessoas_mensagemdiaria, retorna_pessoas_preagendadas,
    salva_mensagem_remota, altera_mensagem_local, atualiza_ano_cliente, print_log, config_zap, retorna_pessoas,
    insere_mensagem_zap, carregar_configuracoes, cria_lock, apaga_lock
    )


def zapautomato():
    
    nome_servico = 'zap_automato'
    #carrega config
    print_log(f'Iniciando',nome_servico)

    if cria_lock(nome_servico):
        print_log('Em execucao', nome_servico)
        return
    
    carregar_configuracoes()
    if os.path.exists("C:/Users/Public/config.json"):
        with open('C:/Users/Public/config.json', 'r') as config_file:
            config = json.load(config_file)
        for cnpj in config['sistema']:
            try:
                dados_cnpj = config['sistema'][cnpj]
                ativo = dados_cnpj['sistema_ativo'] == '1'
                sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
                caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
                data_hora = datetime.datetime.now()
                data_hora_formatada = data_hora.strftime(
                    '%Y_%m_%d_%H_%M_%S')
                print_log(f'Vou validar para enviar mensagem',nome_servico)

                try:
                    con_mysql = parametros.MYSQL_CONNECTION
                    cur = parametros.FIREBIRD_CONNECTION.cursor()
                    cur.execute("select cnpj from empresa where codigo = 1")
                    empresas = cur.fetchall()
                    empresa = [empresa[0] for empresa in empresas]
                    if cnpj != empresa[0]:
                        continue
                except Exception as e:
                    apaga_lock(nome_servico)
                    print_log(f'Não foi possivel verificar a empresa 1: {e}')

                if ativo == 1 and sistema_em_uso == '1':
                    server = "localhost"
                    port = porta_firebird_maxsuport  # Substitua pelo número da porta real, se diferente
                    path = caminho_base_dados_maxsuport
                    user = parametros.USERFB
                    password = parametros.PASSFB
                    dsn = f"{server}/{port}:{path}"
                    fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')
                    conexao = fdb.connect(dsn=dsn, user=user, password=password)
                    cfg_zap = config_zap(conexao)

                    ENVIAR_MENSAGEM_ANIVERSARIO = cfg_zap['ENVIAR_MENSAGEM_ANIVERSARIO'] = 1
                    ENVIAR_MENSAGEM_PROMOCAO    = cfg_zap['ENVIAR_MENSAGEM_PROMOCAO'] = 1
                    ENVIAR_MENSAGEM_DIARIO      = cfg_zap['ENVIAR_MENSAGEM_DIARIO']
                    MENSAGEM_ANIVERSARIO        = cfg_zap['MENSAGEM_ANIVERSARIO']
                    MENSAGEM_PROMOCAO           = cfg_zap['MENSAGEM_PROMOCAO']
                    MENSAGEM_DIARIO             = cfg_zap['MENSAGEM_DIARIO']
                    DIA_MENSAGEM_DIARIA         = cfg_zap['DIA_MENSAGEM_DIARIA']
                    TIME_MENSAGEM_DIARIA        = cfg_zap['TIME_MENSAGEM_DIARIA']
                    ULTIMO_ENVIO_ANIVERSARIO    = cfg_zap['ULTIMO_ENVIO_ANIVERSARIO']
                    ULTIMO_ENVIO_DIARIO         = cfg_zap['ULTIMO_ENVIO_DIARIO']
                    ULTIMO_ENVIO_PROMOCAO       = cfg_zap['ULTIMO_ENVIO_PROMOCAO']                         
                    MENSAGEM_PREAGENDAMENTO     = cfg_zap['MENSAGEM_PREAGENDAMENTO']                         

                    print_log(f'Dados da configuração recebidos',nome_servico)

                    # MENSAGEM DIARIA
                    pessoas = retorna_pessoas_mensagemdiaria(conexao, ENVIAR_MENSAGEM_DIARIO, DIA_MENSAGEM_DIARIA, TIME_MENSAGEM_DIARIA, ULTIMO_ENVIO_DIARIO)
                    for pessoa in pessoas:
                        MENSAGEM_DIARIO = str(MENSAGEM_DIARIO).replace('@cliente',pessoa['FANTASIA'])
                        insere_mensagem_zap(conexao, MENSAGEM_DIARIO, pessoa['CELULAR1'])
                        print_log(f'Registro de mesagem diaria criado para {pessoa["FANTASIA"]}',nome_servico)

                    # MENSAGEM ANIVERSARIO
                    pessoas = retorna_pessoas(conexao)

                    for pessoa in pessoas:
                        ano_atual = datetime.datetime.now().year
                        if pessoa['ANO_ENVIO_MENSAGEM_ANIVERSARIO'] != ano_atual:
                            MENSAGEM_ANIVERSARIO = str(MENSAGEM_ANIVERSARIO).replace('@cliente',pessoa['FANTASIA'])
                            insere_mensagem_zap(conexao, MENSAGEM_ANIVERSARIO, pessoa['CELULAR1'])
                            atualiza_ano_cliente(conexao,pessoa['CODIGO'],ano_atual)
                            print_log(f'Registro de aniversário criado para {pessoa["FANTASIA"]}',nome_servico)
                    
                    # MENSAGEM DE PRE AGENDMANETO
                    pessoas = retorna_pessoas_preagendadas(conexao)

                    for pessoa in pessoas:                        
                        MENSAGEM_PREAGENDAMENTO_FINAL = str(MENSAGEM_PREAGENDAMENTO).replace('@cliente',pessoa['FANTASIA']).replace('@qtddias',str(pessoa['DIAS_RETORNO'])).replace('@servico',pessoa['DESCRICAO'])
                        insere_mensagem_zap(conexao, MENSAGEM_PREAGENDAMENTO_FINAL , pessoa['TELEFONE1'])
                        atualiza_agenda(conexao,pessoa['CODIGO'])
                        print_log(f'Registro de pré agendamento criado para {pessoa["FANTASIA"]}',nome_servico)                            

                    # Salva mensagem em banco remoto e altera status em banco local
                    try:
                        con_fb = parametros.FIREBIRD_CONNECTION
                        cursor = con_fb.cursor()
                        cursor.execute("select mz.codigo, mz.data, mz.hora, mz.mensagem, mz.fone from mensagem_zap mz where mz.status = 'PENDENTE'")
                        rowsMSGs = cursor.fetchall()
                        rows_dict_msg = [dict(zip([column[0] for column in cursor.description], rowmsg)) for rowmsg in rowsMSGs]
                        for row_msg in rows_dict_msg:
                            cod_mensagem = row_msg['CODIGO']
                            data = row_msg['DATA']
                            hora = row_msg['HORA']
                            data_hora = dt.datetime.combine(data, hora)
                            mensagem = row_msg['MENSAGEM']
                            fone = row_msg['FONE']
                            status = 'PENDENTE'
                            cliente_id = cnpj
                            retorno = 'Mensagem Gravada'

                            if salva_mensagem_remota(con_mysql, data_hora, mensagem, fone, status, cliente_id, nome_servico, retorno):
                                altera_mensagem_local(con_fb, cod_mensagem, nome_servico)

                        print_log('Mensagens salvas em servidor remoto', nome_servico)
                        con_fb.close()
                        con_mysql.close()
                        apaga_lock(nome_servico)
                    except Exception as e:
                        print_log(f'Não foi possivel consultar mensagens no banco: {e}', nome_servico)
                        apaga_lock(nome_servico)
                        raise e
            except Exception as a:
                apaga_lock(nome_servico)
                try:
                    if con_fb:
                        con_fb.rollback()
                    if con_mysql:
                        con_mysql.rollback()
                except Exception as e:
                    pass
                print_log(f'{a}',nome_servico)

zapautomato()