from funcoes import print_log, os,json,inicializa_conexao_mysql,threading,datetime
import parametros

class threadverificaremoto(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.salva_json()

    def salva_json(self):
        print_log(f"Carrega configurações da thread" , 'verificaremoto')
        intervalo = -1
        while intervalo == -1:
            path_config_thread = parametros.SCRIPT_PATH + "\\config.json"
            if os.path.exists(path_config_thread):
                with open(path_config_thread, 'r') as config_file:
                    config_thread = json.load(config_file)
            intervalo = config_thread['time_thread_verificaremoto']

        while not self.event.wait(intervalo):
            try:
                parametros.MYSQL_CONNECTION = inicializa_conexao_mysql()

                print_log("Efetua conexão remota" , 'verificaremoto')
                conn = parametros.MYSQL_CONNECTION

                # pego dados do arquivo
                print_log(f"Carrega arquivo {parametros.SCRIPT_PATH}\\cnpj.txt" , 'verificaremoto')
                if os.path.exists(f"{parametros.SCRIPT_PATH}\\cnpj.txt"):
                    with open(f"{parametros.SCRIPT_PATH}\\cnpj.txt", 'r') as config_file:
                        cnpj_list = config_file.read().split('\n')
                cnpj = ''
                for s in cnpj_list:
                    if (cnpj != ''):
                        cnpj += ','
                    cnpj += '"' + s + '"'

                # Consulta ao banco de dados
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    f"""SELECT nome, cnpj, cidade, uf, ativo, sistema_ativo, sistema_em_uso_id, pasta_compartilhada_backup, 
                            caminho_base_dados_maxsuport, caminho_gbak_firebird_maxsuport, porta_firebird_maxsuport, 
                            caminho_base_dados_gfil,caminho_gbak_firebird_gfil,alerta_bloqueio,timer_minutos_backup, porta_firebird_gfil, 
                            ip
                    FROM cliente_cliente where cnpj in ({cnpj})""")
                rows = cursor.fetchall()
                print_log(f"Consultou remoto cnpj's {cnpj}" , 'verificaremoto')

                datahoraagora = datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=-4)))
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE cliente_cliente set ultima_conexao_windows_service = '{datahoraagora}' where cnpj in ({cnpj})")
                print_log(f"Executou update remoto" , 'verificaremoto')
                conn.commit()

                config = {}
                config['sistema'] = {}
                for row in rows:
                    config['sistema'][row['cnpj']] = {"sistema_ativo": str(row['sistema_ativo']),
                                                    "alerta_bloqueio": str(row['alerta_bloqueio']),
                                                    "sistema_em_uso_id": str(row['sistema_em_uso_id']),
                                                    "pasta_compartilhada_backup": str(row['pasta_compartilhada_backup']),
                                                    "caminho_base_dados_maxsuport": str(row['caminho_base_dados_maxsuport']),
                                                    "caminho_gbak_firebird_maxsuport": str(row['caminho_gbak_firebird_maxsuport']),
                                                    "porta_firebird_maxsuport": str(row['porta_firebird_maxsuport']),
                                                    "caminho_base_dados_gfil": str(row['caminho_base_dados_gfil']),
                                                    "caminho_gbak_firebird_gfil": str(row['caminho_gbak_firebird_gfil']),
                                                    "porta_firebird_gfil": str(row['porta_firebird_gfil']),
                                                    "timer_minutos_backup": str(row['timer_minutos_backup']),
                                                    "ip": str(row['ip'])
                                                    }

                with open('C:/Users/Public/config.json', 'w') as configfile:
                    json.dump(config, configfile)
            except Exception as a:
                print_log(a, 'verificaremoto')
