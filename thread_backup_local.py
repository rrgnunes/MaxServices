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
        
        carrega_arquivo_config()
        inicializa_conexao_mysql()
        
        print_log("Efetua conexão remota" , nome_servico)
        conn = parametros.MYSQL_CONNECTION

        print_log("Pega dados local", nome_servico)
        bases_backupedas = []
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

            if ativo:
                if sistema_em_uso == '1':  # maxsuport
                    if pasta_compartilhada_backup and caminho_base_dados_maxsuport and caminho_gbak_firebird_maxsuport and porta_firebird_maxsuport:
                        path = os.path.join(pasta_compartilhada_backup, 'maxsuport', cnpj)
                    
                        if parametros.FIREBIRD_CONNECTION:
                            if not parametros.FIREBIRD_CONNECTION.closed:
                                parametros.FIREBIRD_CONNECTION.close()
                            parametros.FIREBIRD_CONNECTION = None
                        
                        parametros.USERFB = 'maxsuport'
                        parametros.PASSFB = 'oC8qUsDp'
                        parametros.DATABASEFB = caminho_base_dados_maxsuport
                        parametros.PORTFB = 3050


                        if parametros.DATABASEFB == 'None':
                            continue
                        
                        parametros.PATHDLL = verifica_dll_firebird()
                        inicializa_conexao_firebird()
                        conn_fb = parametros.FIREBIRD_CONNECTION
                        cursor_fb = conn_fb.cursor()

                        caminho_arquivo_backup = path
                        comando = f'copy "{caminho_base_dados_maxsuport}" "{caminho_arquivo_backup}"'.replace('/', '\\')

                        cursor_fb.execute('select cnpj from empresa')
                        results = cursor_fb.fetchall()
                        result = [result[0] for result in results]
                        if cnpj in result:
                            if caminho_base_dados_maxsuport.lower() in bases_backupedas:
                                continue
                            bases_backupedas.append(caminho_base_dados_maxsuport.lower())
                            print_log("Inicia backup", nome_servico)
                            os.makedirs(path, exist_ok=True)
                        else:
                            continue
                    else:
                        continue

                elif sistema_em_uso == '2':  # gfil
                    if pasta_compartilhada_backup and caminho_base_dados_gfil and caminho_gbak_firebird_gfil:
                        path = os.path.join(pasta_compartilhada_backup, 'gfil', cnpj)

                        parametros.USERFB = 'GFILMASTER'
                        parametros.PASSFB = 'b32@m451'
                        parametros.DATABASEFB = caminho_base_dados_gfil
                        parametros.PORTFB = 3050

                        parametros.PATHDLL = verifica_dll_firebird()
                        inicializa_conexao_firebird()
                        conn_fb = parametros.FIREBIRD_CONNECTION
                        cursor_fb = conn_fb.cursor()

                        caminho_arquivo_backup = path
                        comando = f'copy "{caminho_base_dados_gfil}" "{caminho_arquivo_backup}"'.replace('/', '\\')

                        cursor_fb.execute(f'select filial, cnpj  from diversos where cnpj = {cnpj} and filial = 1')
                        result = cursor_fb.fetchall()
                        if len(result) < 1:
                            continue
                        print_log("Inicia backup", nome_servico)
                        os.makedirs(path, exist_ok=True)
                    else:
                        continue
                
                cursor_fb.close()
                conn_fb.close()
                subprocess.call(comando, shell=True)
                print_log(f"Executou comando {comando}", nome_servico)

                arquivo_backup = os.path.join(caminho_arquivo_backup, 'dados.fdb') if sistema_em_uso == '1' else os.path.join(caminho_arquivo_backup, 'infolivre.fdb')

                try:
                    arquivo_bck_existe = False
                    if sistema_em_uso == '1':
                        client_dll = verifica_dll_firebird()
                        fdb.load_api(client_dll)

                        conn_fbk = fdb.services.connect(host='localhost/3050', user='sysdba', password='masterkey')
                        arquivo_destino = os.path.join(caminho_arquivo_backup, 'dados.fbk')
                        conn_fbk.backup(arquivo_backup, arquivo_destino, collect_garbage=True)
                        conn_fbk.wait()

                        count = 0
                        while not (os.path.exists(arquivo_destino)) and (count <= 3):
                            time.sleep(3)
                            count += 1

                        if os.path.exists(arquivo_destino):
                            arquivo_bd = arquivo_backup
                            arquivo_backup = arquivo_destino
                        else:
                            raise FileNotFoundError

                        conn_fbk.close()
                        print_log(f'Gerado arquivo de backup: {arquivo_backup}', nome_servico)
                        arquivo_bck_existe = True
                except Exception as e:
                    print_log(f'{e}', nome_servico)

                if sistema_em_uso == '1':
                    if arquivo_bck_existe:
                        nome_arquivo_compactado = f'backup_{data_hora_formatada}_maxsuport.fbk'
                    else:
                        nome_arquivo_compactado = f'backup_{data_hora_formatada}_maxsuport.fdb'
                else:
                    nome_arquivo_compactado = f'backup_{data_hora_formatada}_gfil.fdb'

                # Compacta arquivo
                with open(arquivo_backup, 'rb') as arquivo_in:
                    nome_arquivo_compactado = f'{nome_arquivo_compactado}.xz'
                    with lzma.open(f'{caminho_arquivo_backup}\\{nome_arquivo_compactado}', 'wb', preset=9) as arquivo_out:
                        arquivo_out.writelines(arquivo_in)

                print_log(f"Criou arquivo compactado {nome_arquivo_compactado}", nome_servico)

                datahoraagora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
                cursor = conn.cursor()
                cursor.execute(f"UPDATE cliente_cliente set data_hora_ultimo_backup = '{datahoraagora}' where cnpj = '{cnpj}'")
                print_log("Executou update remoto", nome_servico)
                conn.commit()
                conn.close()

                os.remove(arquivo_backup)
                if arquivo_bck_existe:
                    os.remove(arquivo_bd)

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
        print_log(f'Erro ao gerar backup {e}', nome_servico)


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