from funcoes import *
import parametros
import os
import glob
import lzma
import pathlib
try:
    import dropbox
    from dropbox.files import WriteMode
    from dropbox.exceptions import AuthError
except:
    print_log('erro ao importar dropbox',"backuplocal")

def backup():
    nome_servico = 'thread_backup_local'
    print_log("Carrega configurações da thread",nome_servico)
    try:
        
        inicializa_conexao_mysql()
        carregar_configuracoes()

        print_log("Efetua conexão remota" , nome_servico)
        conn = parametros.MYSQL_CONNECTION

        print_log("Pega dados local", nome_servico)
        for cnpj, dados_cnpj in parametros.CNPJ_CONFIG['sistema'].items():

            # Verifica se conexao esta ativa, se não estiver, conecta novamente
            if not parametros.MYSQL_CONNECTION.is_connected():
                parametros.MYSQL_CONNECTION.connect()
                conn = parametros.MYSQL_CONNECTION
            
            ativo = dados_cnpj['sistema_ativo'] == '1'
            sistema_em_uso = dados_cnpj['sistema_em_uso_id']
            pasta_compartilhada_backup = dados_cnpj['pasta_compartilhada_backup']
            caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
            caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
            porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
            caminho_base_dados_gfil = dados_cnpj['caminho_base_dados_gfil']
            caminho_gbak_firebird_gfil = dados_cnpj['caminho_gbak_firebird_gfil']
            data_hora = datetime.datetime.now()
            data_hora_formatada = data_hora.strftime('%Y_%m_%d_%H_%M_%S')
            timer_minutos_backup = dados_cnpj['timer_minutos_backup']

            conn_fb = parametros.FIREBIRD_CONNECTION
            cursor_fb = conn_fb.cursor()

            if ativo:
                if sistema_em_uso == '1':  # maxsuport
                    if pasta_compartilhada_backup and caminho_base_dados_maxsuport and caminho_gbak_firebird_maxsuport and porta_firebird_maxsuport:
                        path = f'{pasta_compartilhada_backup}\\maxsuport\\{cnpj}'
                        os.makedirs(path, exist_ok=True)

                        caminho_arquivo_backup = path
                        nome_arquivo_compactado = f'backup_{data_hora_formatada}_maxsuport.fdb'
                        comando = f'copy "{caminho_base_dados_maxsuport}" "{caminho_arquivo_backup}"'.replace('/', '\\')

                        cursor_fb.execute(f'select codigo, cnpj from empresa where cnpj = {cnpj} and codigo = 1')
                        result = cursor_fb.fetchall()
                        if len(result) < 1:
                            continue
                        print_log("Inicia backup", nome_servico)

                elif sistema_em_uso == '2':  # gfil
                    if pasta_compartilhada_backup and caminho_base_dados_gfil and caminho_gbak_firebird_gfil:
                        path = f'{pasta_compartilhada_backup}\\gfil\\{cnpj}'
                        os.makedirs(path, exist_ok=True)

                        caminho_arquivo_backup = path
                        nome_arquivo_compactado = f'backup_{data_hora_formatada}_gfil.fdb'
                        comando = f'copy "{caminho_base_dados_gfil}" "{caminho_arquivo_backup}"'.replace('/', '\\')

                        cursor_fb.execute(f'select filial, cnpj  from diversos where cnpj = {cnpj} and filial = 1')
                        result = cursor_fb.fetchall()
                        if len(result) < 1:
                            continue
                        print_log("Inicia backup", nome_servico)
                
                cursor_fb.close()
                subprocess.call(comando, shell=True)
                print_log(f"Executou comando {comando}", nome_servico)

                # Compacta arquivo
                with open(f'{caminho_arquivo_backup}\\dados.fdb', 'rb') as arquivo_in:
                    nome_arquivo_compactado = f'{nome_arquivo_compactado}.xz'
                    with lzma.open(f'{caminho_arquivo_backup}\\{nome_arquivo_compactado}', 'wb', preset=9) as arquivo_out:
                        arquivo_out.writelines(arquivo_in)
                os.remove(f'{caminho_arquivo_backup}\\dados.fdb')
                print_log(f"Criou arquivo compactado {nome_arquivo_compactado}", nome_servico)

                datahoraagora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
                cursor = conn.cursor()
                cursor.execute(f"UPDATE cliente_cliente set data_hora_ultimo_backup = '{datahoraagora}' where cnpj = '{cnpj}'")
                print_log("Executou update remoto", nome_servico)
                conn.commit()

                # Envia arquivo para Dropbox
                pasta_sistema = 'maxsuport' if sistema_em_uso == '1' else 'gfil'
                diretorio_remoto = f'/{cnpj}/backup/{pasta_sistema}'

                try:
                    arquivo_local = f'{caminho_arquivo_backup}\\{nome_arquivo_compactado}'
                    arquivo_remoto = f'{diretorio_remoto}/{nome_arquivo_compactado}'

                    configuracao = select("select * from configuracao_configuracao")[0]
                    ACCESS_TOKEN_DROP_BOX = configuracao['access_token_drop_box']
                    REFRESH_TOKEN_DROP_BOX = configuracao['refresh_token_drop_box']
                    APP_KEY_DROP_BOX = configuracao['app_key_drop_box']
                    APP_SECRET_DROP_BOX = configuracao['app_secret_drop_box']

                    obj_dropbox = dropbox.Dropbox(
                        oauth2_access_token=ACCESS_TOKEN_DROP_BOX,
                        oauth2_refresh_token=REFRESH_TOKEN_DROP_BOX,
                        app_key=APP_KEY_DROP_BOX,
                        app_secret=APP_SECRET_DROP_BOX
                    )
                    obj_dropbox.check_and_refresh_access_token()

                    sql = '''update configuracao_configuracao set access_token_drop_box = %s, refresh_token_drop_box = %s'''
                    update(sql, (obj_dropbox._oauth2_access_token, obj_dropbox._oauth2_refresh_token))

                    with open(arquivo_local, 'rb') as arquivo:
                        obj_dropbox.files_upload(arquivo.read(), arquivo_remoto, mode=WriteMode('overwrite'))

                    print_log(f"Arquivo {arquivo_local} enviado para o Dropbox em {arquivo_remoto}", nome_servico)

                    num_arquivos_a_manter = int(timer_minutos_backup)
                    try:
                        result = obj_dropbox.files_list_folder(diretorio_remoto)
                        arquivos_na_pasta = result.entries
                        print_log(f'Quantidade de arquivos no DropBox: {len(arquivos_na_pasta)}', nome_servico)
                    except dropbox.exceptions.ApiError as e:
                        print_log(f"Erro ao listar arquivos na pasta remota: {e}", nome_servico)
                        arquivos_na_pasta = []

                    if len(arquivos_na_pasta) > num_arquivos_a_manter:
                        arquivos_na_pasta.sort(key=lambda entry: entry.server_modified)
                        qtd_arquivos_excesso = len(arquivos_na_pasta) - num_arquivos_a_manter
                        arquivos_em_excesso = arquivos_na_pasta[:qtd_arquivos_excesso]
                        try:
                            for arquivo in arquivos_em_excesso:
                                obj_dropbox.files_delete_v2(arquivo.path_display)
                                print_log(f"Arquivo excluído remoto: {arquivo.path_display}.", nome_servico)
                            # obj_dropbox.files_delete_v2(arquivos_na_pasta[0].path_display)
                            # print_log(f"Arquivo mais antigo {arquivos_na_pasta[0].path_display} excluído.","backuplocal")
                        except dropbox.exceptions.ApiError as e:
                            print_log(f"Erro ao excluir o arquivo mais antigo: {e}", nome_servico)

                    extensao = '.xz'
                    arquivos = glob.glob(os.path.join(caminho_arquivo_backup, '*' + extensao))
                    arquivos.sort(key=lambda arquivo: os.path.getmtime(arquivo))

                    if len(arquivos) > num_arquivos_a_manter:
                        num_arquivos_excedentes = len(arquivos) - num_arquivos_a_manter
                        arquivos_excedentes = arquivos[:num_arquivos_excedentes]
                        for arquivo in arquivos_excedentes:
                            os.remove(arquivo)
                            print_log(f"Arquivo excluído local: {arquivo}", nome_servico)

                    print_log('Termina backup', nome_servico)
                except Exception as e:
                    print_log(e, nome_servico)
                finally:
                    print_log(f'Finalizado {data_hora_formatada}', nome_servico)
                    obj_dropbox.close()
    except Exception as e:
        print_log(e, nome_servico)


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            backup()
        except Exception as e:
            print_log(f'Ocorreu um erro ao executar - motivo:{e}')
        finally:
            remover_bloqueio(nome_script)