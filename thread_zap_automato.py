import fdb
from funcoes import os,json,datetime,atualiza_agenda,retorna_pessoas_preagendadas, envia_mensagem, atualiza_ano_cliente, print_log, config_zap, retorna_pessoas, insere_mensagem_zap
import parametros


def zapautomato():
    nome_servico = 'zap automato'
    #carrega config
    print_log(f'Iniciando',nome_servico)
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
                    ENVIAR_MENSAGEM_DIARIO      = cfg_zap['ENVIAR_MENSAGEM_DIARIO'] = 1
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
                        MENSAGEM_PREAGENDAMENTO = str(MENSAGEM_PREAGENDAMENTO).replace('@cliente',pessoa['FANTASIA']).replace('@qtddias',str(pessoa['DIAS_RETORNO'])).replace('@servico',pessoa['DESCRICAO'])
                        insere_mensagem_zap(conexao, MENSAGEM_PREAGENDAMENTO, pessoa['CELULAR1'])
                        atualiza_agenda(conexao,pessoa['CODIGO'])
                        print_log(f'Registro de pré agendamento criado para {pessoa["FANTASIA"]}',nome_servico)                            

                    envia_mensagem(conexao,cnpj)
            except Exception as a:
                print_log(f'{a}',nome_servico)

zapautomato()