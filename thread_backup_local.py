from funcoes import *

try:
    import dropbox
    from dropbox.files import WriteMode
    from dropbox.exceptions import AuthError
except:
    print('erro ao importar dropbox')


# thread do backup
class threadbackuplocal(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.backup()
        
    def backup(self):
        print_log(f"Carrega configurações da thread - backuplocal")
        intervalo = -1
        while intervalo == -1:
            path_config_thread = SCRIPT_PATH + "/config.json"
            if os.path.exists(path_config_thread):
                with open(path_config_thread, 'r') as config_file:
                    config_thread = json.load(config_file)
                    intervalo = config_thread['time_thread_backuplocal']

        while not self.event.wait(intervalo):
            try:
                conn = mysql.connector.connect(
                    host=HOSTMYSQL,
                    user=USERMYSQL,
                    password=PASSMYSQL,
                    database=BASEMYSQL
                )
                
                print_log(f"Pega dados local - backuplocal")
                if os.path.exists("C:/Users/Public/config.json"):
                    with open('C:/Users/Public/config.json', 'r') as config_file:
                        config = json.load(config_file)
                    for cnpj in config['sistema']:
                        dados_cnpj = config['sistema'][cnpj]
                        ativo = dados_cnpj['sistema_ativo'] == '1'
                        sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                        pasta_compartilhada_backup = dados_cnpj['pasta_compartilhada_backup']
                        caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                        caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
                        porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
                        caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil']
                        caminho_gbak_firebird_gfil = dados_cnpj['caminho_gbak_firebird_gfil']
                        data_hora = datetime.datetime.now()
                        data_hora_formatada = data_hora.strftime(
                            '%Y_%m_%d_%H_%M_%S')
                        timer_minutos_backup = parametros['timer_minutos_backup']

                        if ativo:
                            print_log(f"Inicia backup - backuplocal")
                            if sistema_em_uso == '1':  # maxsuport
                                if pasta_compartilhada_backup != '' and \
                                        caminho_base_dados_maxsuport != '' and \
                                        caminho_gbak_firebird_maxsuport != '' and \
                                        porta_firebird_maxsuport != '':
                                    path = f'{pasta_compartilhada_backup}/maxsuport'
                                    if not os.path.exists(path):
                                        os.mkdir(path)
                                    path = f'{pasta_compartilhada_backup}/maxsuport/{cnpj}'
                                    if not os.path.exists(path):
                                        os.mkdir(path)

                                    caminho_arquivo_backup = path
                                    usuario = parametros.USERFB
                                    senha = parametros.PASSFB
                                    banco_de_dados = caminho_base_dados_maxsuport
                                    nome_arquivo_compactado = f'backup_{data_hora_formatada}_maxsuport.fdb'
                                    nome_arquivo = 'Dados.fdb'
                                    # comando = f'"{caminho_gbak_firebird_maxsuport}/gbak.exe" -t -v -g -limbo -user {usuario} -password {senha} {banco_de_dados} {caminho_arquivo_backup}/{nome_arquivo}'
                                    comando = f'copy {banco_de_dados} {caminho_arquivo_backup}'
                                    comando = comando.replace('/', '\\')

                            elif sistema_em_uso == '2':  # gfil
                                if pasta_compartilhada_backup != '' and \
                                        caminho_base_dados_gfil != '' and \
                                        caminho_gbak_firebird_gfil != '':
                                    path = f'{pasta_compartilhada_backup}/gfil'
                                    if not os.path.exists(path):
                                        os.mkdir(path)
                                    path = f'{pasta_compartilhada_backup}/gfil/{cnpj}'
                                    if not os.path.exists(path):
                                        os.mkdir(path)
                                    caminho_arquivo_backup = path
                                    usuario = "GFILMASTER"
                                    senha = "b32@m451"
                                    banco_de_dados = caminho_base_dados_gfil
                                    nome_arquivo_compactado = f'backup_{data_hora_formatada}_gfil.fdb'
                                    nome_arquivo = 'Infolivre.fdb'
                                    # comando = f'"{caminho_gbak_firebird_gfil}/gbak.exe" -t -v -g -limbo -user {usuario} -password {senha} {banco_de_dados} {caminho_arquivo_backup}/{nome_arquivo}'
                                    comando = f'copy {banco_de_dados} {caminho_arquivo_backup}'
                                    comando = comando.replace('/', '\\')

                            subprocess.call(comando, shell=True)
                            print_log(f"Executou comando {comando} - backuplocal")
                            # compacta arquivo
                            with open(f'{caminho_arquivo_backup}/{nome_arquivo}', 'rb') as arquivo_in:
                                nome_arquivo_compactado = f'{nome_arquivo_compactado}.xz'
                                with lzma.open(f'{caminho_arquivo_backup}/{nome_arquivo_compactado}', 'wb', preset=9) as arquivo_out:
                                    arquivo_out.writelines(arquivo_in)
                            os.remove(f'{caminho_arquivo_backup}/{nome_arquivo}')
                            print_log(
                                f"criou arquivo compactado {nome_arquivo_compactado} - backuplocal")
                            datahoraagora = datetime.datetime.now(
                                datetime.timezone(datetime.timedelta(hours=-3)))
                            cursor = conn.cursor()
                            cursor.execute(
                                f"UPDATE cliente_cliente set data_hora_ultimo_backup = '{datahoraagora}' where cnpj = '{cnpj}'")
                            print_log(f"Executou update remoto - backuplocal")
                            conn.commit()
                            conn.close()

                            # Envia arquivo para servidor
                            # Configurações de conexão FTP
                            # hostname = 'maxsuport.vps-kinghost.net'
                            # username = 'dinheiro'
                            # password = 'MT49T3.6%B'

                            pasta_sistema = 'gfil'
                            if sistema_em_uso == '1':  # maxsuport
                                pasta_sistema = 'maxsuport'

                            # Caminho de destino no servidor FTP
                            # diretorio_remoto = f'/home/dinheiro/maxadmin/maxadmin/arquivos/{cnpj}/backup/{pasta_sistema}'
                            diretorio_remoto = f'/{cnpj}/backup/{pasta_sistema}'

                            try:
                                # Caminho local do arquivo que você deseja fazer upload
                                arquivo_local = f'{caminho_arquivo_backup}/{nome_arquivo_compactado}'       

                                # Caminho remoto no Dropbox onde o arquivo será salvo
                                arquivo_remoto = f'{diretorio_remoto}/{nome_arquivo_compactado}'

                                # Configurar a autenticação com o Dropbox
                                # efetua refresh e tudo
                                configuracao = select("select * from configuracao_configuracao")[0]
                                ACCESS_TOKEN_DROP_BOX = configuracao['access_token_drop_box']
                                REFRESH_TOKEN_DROP_BOX = configuracao['refresh_token_drop_box']
                                APP_KEY_DROP_BOX = configuracao['app_key_drop_box']
                                APP_SECRET_DROP_BOX = configuracao['app_secret_drop_box']
                                data_agora = datetime.datetime.now()

                                obj_dropbox = dropbox.Dropbox(oauth2_access_token=ACCESS_TOKEN_DROP_BOX,
                                                              oauth2_refresh_token=REFRESH_TOKEN_DROP_BOX,
                                                              app_key=APP_KEY_DROP_BOX,
                                                              app_secret=APP_SECRET_DROP_BOX)
                                obj_dropbox.check_and_refresh_access_token()
                                sql = '''update configuracao_configuracao set access_token_drop_box = %s,
                                                  refresh_token_drop_box = %s'''

                                update(sql,(obj_dropbox._oauth2_access_token,
                                            obj_dropbox._oauth2_refresh_token))


                                # if (configuracao['expira_em'] - data_agora) < datetime.timedelta(minutes=2):
                                #     obj_dropbox = dropbox.Dropbox(oauth2_refresh_token=configuracao['refresh_token_drop_box'], app_key=configuracao['app_key_drop_box'], app_secret=configuracao['app_secret_drop_box'])
                                #     # Obtendo um novo token de acesso
                                #     novo_access_token = obj_dropbox.auth_oauth2_token_from_refresh()
                                #     ACCESS_TOKEN_DROP_BOX = novo_access_token
                                #     sql = '''update configuracao_configuracao set access_token_drop_box = %s'''

                                #     insert(sql,(novo_access_token))

                                # obj_dropbox = dropbox.Dropbox(ACCESS_TOKEN_DROP_BOX)
                
                                # Fazer upload do arquivo
                                with open(arquivo_local, 'rb') as arquivo:
                                    obj_dropbox.files_upload(arquivo.read(), arquivo_remoto, mode=WriteMode('overwrite'))

                                print_log(f"Arquivo {arquivo_local} enviado para o Dropbox em {arquivo_remoto} - backuplocal")                                
                                # # Cria uma instância do cliente FTP
                                # cliente_ftp = FTP()

                                # # Conecta ao servidor FTP
                                # cliente_ftp.connect(hostname)
                                # cliente_ftp.login(username, password)

                                # # Cria pastas nao existentes
                                # cliente_ftp.cwd(
                                #     '/home/dinheiro/maxadmin/maxadmin/arquivos/')
                                # if not f'{cnpj}' in cliente_ftp.nlst():
                                #     cliente_ftp.mkd(f'{cnpj}')

                                # cliente_ftp.cwd(
                                #     f'/home/dinheiro/maxadmin/maxadmin/arquivos/{cnpj}/backup/')
                                # if not f'{pasta_sistema}' in cliente_ftp.nlst():
                                #     cliente_ftp.mkd(f'{pasta_sistema}')

                                # # Entra no diretório remoto
                                # cliente_ftp.cwd(diretorio_remoto)

                                # # Abre o arquivo local em modo de leitura binária
                                # with open(arquivo_local, 'rb') as arquivo:
                                #     # Envia o arquivo para o servidor remoto
                                #     cliente_ftp.storbinary(
                                #         f'STOR {nome_arquivo_compactado}', arquivo)

                                print_log(
                                    'Arquivo enviado com sucesso - backuplocal')

                                num_arquivos_a_manter = int(timer_minutos_backup)
                                # Consultar a lista de arquivos na pasta remota
                                try:
                                    result = obj_dropbox.files_list_folder(diretorio_remoto)
                                    arquivos_na_pasta = result.entries
                                except dropbox.exceptions.ApiError as e:
                                    print(f"Erro ao listar arquivos na pasta remota: {e}")
                                    arquivos_na_pasta = []

                                # Verificar se há mais de 30 arquivos e excluir o mais antigo se necessário
                                if len(arquivos_na_pasta) > num_arquivos_a_manter:
                                    # Ordenar os arquivos pela data de modificação (o mais antigo primeiro)
                                    arquivos_na_pasta.sort(key=lambda entry: entry.server_modified)

                                    # Excluir o arquivo mais antigo
                                    try:
                                        obj_dropbox.files_delete_v2(arquivos_na_pasta[0].path_display)
                                        print_log(f"Arquivo mais antigo {arquivos_na_pasta[0].path_display} excluído.")
                                    except dropbox.exceptions.ApiError as e:
                                        print(f"Erro ao excluir o arquivo mais antigo: {e}")

                                # # Extensão dos arquivos que deseja excluir
                                extensao = '.xz'
                                
                                # # Lista todos os arquivos na pasta remota

                                # lista_arquivos = cliente_ftp.nlst()

                                # # Filtra os arquivos pela extensão desejada
                                # arquivos_filtrados = [
                                #     arquivo for arquivo in lista_arquivos if arquivo.endswith(extensao)]
                                # # Verifica se existem mais de max_arquivos arquivos
                                # if len(arquivos_filtrados) > num_arquivos_a_manter:
                                #     # Classifica os arquivos pela data de modificação
                                #     arquivos_filtrados.sort(
                                #         key=lambda arquivo: cliente_ftp.voidcmd('MDTM ' + arquivo)[4:])

                                #     # Calcula o número de arquivos excedentes
                                #     num_arquivos_excedentes = len(
                                #         arquivos_filtrados) - num_arquivos_a_manter

                                #     # Remove os arquivos excedentes
                                #     arquivos_excedentes = arquivos_filtrados[:num_arquivos_excedentes]
                                #     for arquivo in arquivos_excedentes:
                                #         cliente_ftp.delete(arquivo)
                                #         print_log(
                                #             f"Arquivo excluído remoto: {arquivo}")

                                # Lista todos os arquivos na pasta com a extensão desejada
                                arquivos = glob.glob(os.path.join(
                                    caminho_arquivo_backup, '*' + extensao))

                                # Ordena os arquivos pela data de modificação
                                arquivos.sort(
                                    key=lambda arquivo: os.path.getmtime(arquivo))

                                # Verifica se existem mais de max_arquivos arquivos
                                if len(arquivos) > num_arquivos_a_manter:
                                    # Calcula o número de arquivos excedentes
                                    num_arquivos_excedentes = len(
                                        arquivos) - num_arquivos_a_manter

                                    # Remove os arquivos excedentes
                                    arquivos_excedentes = arquivos[:num_arquivos_excedentes]
                                    for arquivo in arquivos_excedentes:
                                        os.remove(arquivo)
                                        print_log(
                                            f"Arquivo excluído local: {arquivo}")

                                print_log('termina backup - backuplocal')
                            except Exception as e:
                                print_log(e)
                            finally:
                                print_log('Finalizado - backuplocal')
                                # Fecha a conexão FTP
                                obj_dropbox.close()

            except Exception as a:
                # self.logger.error(f"{self._svc_name_} {a}.")
                print_log(a)

            #time.sleep(intervalo)
