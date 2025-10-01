import os
import sys
import fdb
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes import (
    atualiza_agenda, retorna_pessoas_mensagemdiaria, retorna_pessoas_preagendadas,
    salva_mensagem_remota, altera_mensagem_local, atualiza_ano_cliente, print_log, config_zap, retorna_pessoas,
    insere_mensagem_zap, retorna_pessoas_lembrete, pode_executar, criar_bloqueio, remover_bloqueio,
    inicializa_conexao_firebird, inicializa_conexao_mysql, carrega_arquivo_config
    )
from data.thread_zap_automato.listas import selecionar_frase_diaria


def zapautomato():
    
    nome_servico = os.path.basename(sys.argv[0]).replace('.py', '')
    #carrega config
    print_log(f'Iniciando', nome_servico)
    inicializa_conexao_mysql()

    carrega_arquivo_config()
    config = parametros.CNPJ_CONFIG
    try:
        for cnpj in config['sistema']:
            try:

                dados_cnpj = config['sistema'][cnpj]
                ativo = dados_cnpj['sistema_ativo'] == '1'
                sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
                caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
                data_hora = datetime.datetime.now()

                print_log(f'Vou validar para enviar mensagem em empresa cnpj: {cnpj}', nome_servico)

                try:
                    con_mysql = parametros.MYSQL_CONNECTION

                    parametros.DATABASEFB = caminho_base_dados_maxsuport
                    if (parametros.DATABASEFB == None) or (parametros.DATABASEFB == "None"):
                        continue

                    if not os.path.exists(parametros.DATABASEFB):
                        print_log('Banco de dados não encontrando, pulando execução...')
                        continue
                    
                    parametros.PORTFB = porta_firebird_maxsuport
                    parametros.PATHDLL = f'{caminho_gbak_firebird_maxsuport}/fbclient.dll'
                    inicializa_conexao_firebird()
                    cur = parametros.FIREBIRD_CONNECTION.cursor()

                    cur.execute("select cnpj from empresa where codigo = 1")
                    empresas = cur.fetchall()
                    empresa = [empresa[0] for empresa in empresas]

                    if cnpj != empresa[0]:
                        parametros.FIREBIRD_CONNECTION.close()
                        parametros.FIREBIRD_CONNECTION = None
                        continue
                except Exception as e:
                    print_log(f'Não foi possivel verificar a empresa 1: {e}', nome_servico)
                    return

                if ativo == 1 and sistema_em_uso == '1':
                    server = "localhost"
                    port = porta_firebird_maxsuport
                    path = caminho_base_dados_maxsuport
                    user = parametros.USERFB
                    password = parametros.PASSFB
                    dsn = f"{server}/{port}:{path}"
                    fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')
                    conexao = fdb.connect(dsn=dsn, user=user, password=password)
                    cfg_zap = config_zap(conexao)

                    ENVIAR_MENSAGEM_ANIVERSARIO = cfg_zap['ENVIAR_MENSAGEM_ANIVERSARIO'] = 1
                    ENVIAR_MENSAGEM_PROMOCAO    = cfg_zap['ENVIAR_MENSAGEM_PROMOCAO'] = 1
                    ENVIAR_MENSAGEM_LEMBRETE    = cfg_zap['ENVIAR_MENSAGEM_LEMBRETE']
                    ENVIAR_MENSAGEM_DIARIO      = cfg_zap['ENVIAR_MENSAGEM_DIARIO']
                    DIA_MENSAGEM_DIARIA         = cfg_zap['DIA_MENSAGEM_DIARIA']
                    TIME_MENSAGEM_DIARIA        = cfg_zap['TIME_MENSAGEM_DIARIA']
                    TIME_MENSAGEM_LEMBRETE      = cfg_zap['TIME_MENSAGEM_LEMBRETE']
                    ULTIMO_ENVIO_ANIVERSARIO    = cfg_zap['ULTIMO_ENVIO_ANIVERSARIO']
                    ULTIMO_ENVIO_DIARIO         = cfg_zap['ULTIMO_ENVIO_DIARIO']
                    ULTIMO_ENVIO_PROMOCAO       = cfg_zap['ULTIMO_ENVIO_PROMOCAO']                         
                    MENSAGEM_ANIVERSARIO        = cfg_zap['MENSAGEM_ANIVERSARIO']
                    MENSAGEM_PROMOCAO           = cfg_zap['MENSAGEM_PROMOCAO']
                    MENSAGEM_DIARIO             = cfg_zap['MENSAGEM_DIARIO']
                    MENSAGEM_PREAGENDAMENTO     = cfg_zap['MENSAGEM_PREAGENDAMENTO']
                    MENSAGEM_LEMBRETE           = cfg_zap['MENSAGEM_LEMBRETE']               

                    print_log(f'Dados da configuração recebidos', nome_servico)

                    # MENSAGEM DIARIA
                    pessoas = retorna_pessoas_mensagemdiaria(conexao, ENVIAR_MENSAGEM_DIARIO, DIA_MENSAGEM_DIARIA, TIME_MENSAGEM_DIARIA, ULTIMO_ENVIO_DIARIO)
                    for pessoa in pessoas:
                        MENSAGEM_DIARIO = selecionar_frase_diaria()
                        MENSAGEM_DIARIO_FINAL = str(MENSAGEM_DIARIO).replace('@cliente',pessoa['FANTASIA'])
                        insere_mensagem_zap(conexao, MENSAGEM_DIARIO_FINAL, pessoa['CELULAR1'].replace('(','').replace(')','').replace('-','').replace(' ',''))
                        print_log(f'Registro de mesagem diaria criado para {pessoa["FANTASIA"]}', nome_servico)

                    # MENSAGEM ANIVERSARIO
                    pessoas = retorna_pessoas(conexao)
                    for pessoa in pessoas:
                        ano_atual = datetime.datetime.now().year
                        if pessoa['ANO_ENVIO_MENSAGEM_ANIVERSARIO'] != ano_atual:
                            MENSAGEM_ANIVERSARIO_FINAL = str(MENSAGEM_ANIVERSARIO).replace('@cliente',pessoa['FANTASIA'])
                            insere_mensagem_zap(conexao, MENSAGEM_ANIVERSARIO_FINAL, pessoa['CELULAR1'].replace('(','').replace(')','').replace('-','').replace(' ',''))
                            atualiza_ano_cliente(conexao,pessoa['CODIGO'],ano_atual)
                            print_log(f'Registro de aniversário criado para {pessoa["FANTASIA"]}', nome_servico)
                    
                    # MENSAGEM DE PRE AGENDAMENTO
                    pessoas = retorna_pessoas_preagendadas(conexao)
                    for pessoa in pessoas:
                        MENSAGEM_PREAGENDAMENTO_FINAL = str(MENSAGEM_PREAGENDAMENTO).replace('@cliente',pessoa['FANTASIA']).replace('@qtddias',str(pessoa['DIAS_RETORNO'])).replace('@servico',pessoa['DESCRICAO'])
                        insere_mensagem_zap(conexao, MENSAGEM_PREAGENDAMENTO_FINAL , pessoa['TELEFONE1'].replace('(','').replace(')','').replace('-','').replace(' ',''))
                        atualiza_agenda(conexao,pessoa['CODIGO'], 'pre_agendamento')
                        print_log(f'Registro de pré agendamento criado para {pessoa["FANTASIA"]}', nome_servico)     

                    # MENSAGEM DE LEMBRETE 
                    if ENVIAR_MENSAGEM_LEMBRETE == 1:
                        pessoas = retorna_pessoas_lembrete(conexao, TIME_MENSAGEM_LEMBRETE)
                        for pessoa in pessoas:
                            data_agendada = pessoa['DATA']
                            hora_agendada = data_agendada.time().replace(microsecond=0)
                            mensagem_lembrete_final = str(MENSAGEM_LEMBRETE).replace('@cliente', pessoa['FANTASIA']).replace('@servico', pessoa['DESCRICAO']).replace('@hora', str(hora_agendada))
                            insere_mensagem_zap(conexao, mensagem_lembrete_final, pessoa['TELEFONE1'].replace('(','').replace(')','').replace('-','').replace(' ',''))
                            atualiza_agenda(conexao, pessoa['CODIGO'], 'lembrete')
                            print_log(f'Registro de lembrete criado para {pessoa["FANTASIA"]}', nome_servico)
                    
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
                            data_hora = datetime.datetime.combine(data, hora)
                            mensagem = row_msg['MENSAGEM']
                            fone = row_msg['FONE']
                            status = 'PENDENTE'
                            cliente_id = cnpj
                            retorno = 'Mensagem Gravada'

                            if salva_mensagem_remota(con_mysql, data_hora, mensagem, fone, status, cliente_id, nome_servico, retorno):
                                altera_mensagem_local(con_fb, cod_mensagem, nome_servico)

                        print_log('Mensagens salvas em servidor remoto', nome_servico)
                    except Exception as e:
                        print_log(f'Não foi possivel consultar mensagens no banco: {e}', nome_servico)
                        raise e
                    finally:
                        if not con_fb.closed:
                            con_fb.close()
                            parametros.FIREBIRD_CONNECTION = None
            except Exception as a:
                try:
                    if con_fb:
                        con_fb.rollback()
                        con_fb.close()
                    if con_mysql:
                        con_mysql.rollback()
                        con_mysql.close()
                except Exception as e:
                    pass
                print_log(f'{a}', nome_servico)
    finally:
        if con_mysql.is_connected():
            con_mysql.close()
            parametros.MYSQL_CONNECTION = None



if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')

    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            zapautomato()
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar - motivo: {e}', nome_script)
        finally:
            remover_bloqueio(nome_script)