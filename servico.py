import win32serviceutil
import win32service
import time
import mysql.connector
import os
import psutil
import threading
import logging
import socket
import subprocess
import psutil
import json
import datetime
import lzma
import glob
import fdb
import zlib
from ftplib import FTP
import logging
from logging.handlers import RotatingFileHandler

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'

# Configuração do logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
# Configuração do handler
log_file = SCRIPT_PATH + 'log.log'
max_bytes = 1024 * 1024  # 1 MB
backup_count = 3  # Número de arquivos de backup a serem mantidos
handler = RotatingFileHandler(
    log_file, maxBytes=max_bytes, backupCount=backup_count)
handler.setLevel(logging.DEBUG)

# Formatação do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Adicionando o handler ao logger
logger.addHandler(handler)


class threadverificaremoto(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.interval):
            self.do_something()
            time.sleep(self.interval)

    def do_something(self):
        # Conexão com o banco de dados
        try:
            print_log("Efetua conexão remota - verificaremoto")
            conn = mysql.connector.connect(
                host="177.153.69.3",
                user="dinheiro",
                password="MT49T3.6%B",
                database="maxservices"
            )

            # pego dados do arquivo
            print_log(
                f"Carrega arquivo {SCRIPT_PATH}cnpj.txt - verificaremoto")
            if os.path.exists(f"{SCRIPT_PATH}cnpj.txt"):
                with open(f"{SCRIPT_PATH}cnpj.txt", 'r') as config_file:
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
            print_log(f"Consultou remoto cnpj's {cnpj} - verificaremoto")

            datahoraagora = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=-4)))
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE cliente_cliente set ultima_conexao_windows_service = '{datahoraagora}' where cnpj in ({cnpj})")
            print_log(f"Executou update remoto - verificaremoto")
            conn.commit()
            conn.close()

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
            # self.logger.error(f"{self._svc_name_} {a}.")
            print_log(a)


# thread do backup
class threadbackuplocal(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.interval):
            self.backup()
            time.sleep(self.interval)

    def backup(self):
        try:
            conn = mysql.connector.connect(
                host="177.153.69.3",
                user="dinheiro",
                password="MT49T3.6%B",
                database="maxservices"
            )
            print_log(f"Pega dados local - backuplocal")
            if os.path.exists("C:/Users/Public/config.json"):
                with open('C:/Users/Public/config.json', 'r') as config_file:
                    config = json.load(config_file)
                for cnpj in config['sistema']:
                    parametros = config['sistema'][cnpj]
                    ativo = parametros['sistema_ativo'] == '1'
                    sistema_em_uso = parametros['sistema_em_uso_id']
                    pasta_compartilhada_backup = parametros['pasta_compartilhada_backup']
                    caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                    caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                    porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                    caminho_base_dados_gfil = parametros['caminho_base_dados_gfil']
                    caminho_gbak_firebird_gfil = parametros['caminho_gbak_firebird_gfil']
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
                                usuario = "sysdba"
                                senha = "masterkey"
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
                        hostname = 'maxsuport.vps-kinghost.net'
                        username = 'dinheiro'
                        password = 'MT49T3.6%B'

                        pasta_sistema = 'gfil'
                        if sistema_em_uso == '1':  # maxsuport
                            pasta_sistema = 'maxsuport'

                        # Caminho do arquivo local que você deseja enviar
                        arquivo_local = f'{caminho_arquivo_backup}/{nome_arquivo_compactado}'

                        # Caminho de destino no servidor FTP
                        diretorio_remoto = f'/home/dinheiro/maxadmin/maxadmin/arquivos/{cnpj}/backup/{pasta_sistema}'

                        try:
                            # Cria uma instância do cliente FTP
                            cliente_ftp = FTP()

                            # Conecta ao servidor FTP
                            cliente_ftp.connect(hostname)
                            cliente_ftp.login(username, password)

                            # Cria pastas nao existentes
                            cliente_ftp.cwd(
                                '/home/dinheiro/maxadmin/maxadmin/arquivos/')
                            if not f'{cnpj}' in cliente_ftp.nlst():
                                cliente_ftp.mkd(f'{cnpj}')

                            cliente_ftp.cwd(
                                f'/home/dinheiro/maxadmin/maxadmin/arquivos/{cnpj}/backup/')
                            if not f'{pasta_sistema}' in cliente_ftp.nlst():
                                cliente_ftp.mkd(f'{pasta_sistema}')

                            # Entra no diretório remoto
                            cliente_ftp.cwd(diretorio_remoto)

                            # Abre o arquivo local em modo de leitura binária
                            with open(arquivo_local, 'rb') as arquivo:
                                # Envia o arquivo para o servidor remoto
                                cliente_ftp.storbinary(
                                    f'STOR {nome_arquivo_compactado}', arquivo)

                            print_log(
                                'Arquivo enviado com sucesso - backuplocal')

                            # Extensão dos arquivos que deseja excluir
                            extensao = '.xz'
                            num_arquivos_a_manter = int(timer_minutos_backup)
                            # Lista todos os arquivos na pasta remota

                            lista_arquivos = cliente_ftp.nlst()

                            # Filtra os arquivos pela extensão desejada
                            arquivos_filtrados = [
                                arquivo for arquivo in lista_arquivos if arquivo.endswith(extensao)]
                            # Verifica se existem mais de max_arquivos arquivos
                            if len(arquivos_filtrados) > num_arquivos_a_manter:
                                # Classifica os arquivos pela data de modificação
                                arquivos_filtrados.sort(
                                    key=lambda arquivo: cliente_ftp.voidcmd('MDTM ' + arquivo)[4:])

                                # Calcula o número de arquivos excedentes
                                num_arquivos_excedentes = len(
                                    arquivos_filtrados) - num_arquivos_a_manter

                                # Remove os arquivos excedentes
                                arquivos_excedentes = arquivos_filtrados[:num_arquivos_excedentes]
                                for arquivo in arquivos_excedentes:
                                    cliente_ftp.delete(arquivo)
                                    print_log(
                                        f"Arquivo excluído remoto: {arquivo}")

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
                        finally:
                            # Fecha a conexão FTP
                            cliente_ftp.quit()

        except Exception as a:
            # self.logger.error(f"{self._svc_name_} {a}.")
            print_log(a)

# thread do alerta bloqueio


class threadalertabloqueio(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.interval):
            self.alertabloqueio()
            time.sleep(self.interval)

    def alertabloqueio(self):
        # Conexão com o banco de dados
        try:
            print_log(f"pega dados local - alertabloqueio")
            if os.path.exists("C:/Users/Public/config.json"):
                with open('C:/Users/Public/config.json', 'r') as config_file:
                    config = json.load(config_file)
                for cnpj in config['sistema']:
                    parametros = config['sistema'][cnpj]
                    alerta_bloqueio = parametros['alerta_bloqueio'] == '1'

                    if alerta_bloqueio:
                        exibe_alerta(
                            "2Seu sistema poderá ser bloqueado em breve por inadimplência de mensalidades.\nContatos:\n(66) 99926-4708 / 99635-3159 / 99935-3355;")

        except Exception as a:
            # self.logger.error(f"{self._svc_name_} {a}.")
            print_log(a)


class threadxmlcontador(threading.Thread):
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.interval):
            self.xmlcontador()
            time.sleep(self.interval)

    def xmlcontador(self):
        # Conexão com o banco de dados
        try:
            print_log(f"pega dados local - xmlcontador")
            if os.path.exists("C:/Users/Public/config.json"):
                with open('C:/Users/Public/config.json', 'r') as config_file:
                    config = json.load(config_file)
                for cnpj in config['sistema']:
                    parametros = config['sistema'][cnpj]
                    ativo = parametros['sistema_ativo'] == '1'
                    sistema_em_uso = parametros['sistema_em_uso_id']
                    pasta_compartilhada_backup = parametros['pasta_compartilhada_backup']
                    caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                    caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                    porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                    caminho_base_dados_gfil = parametros['caminho_base_dados_gfil']
                    caminho_gbak_firebird_gfil = parametros['caminho_gbak_firebird_gfil']
                    porta_firebird_gfil = parametros['porta_firebird_gfil']
                    data_hora = datetime.datetime.now()
                    data_hora_formatada = data_hora.strftime(
                        '%Y_%m_%d_%H_%M_%S')
                    timer_minutos_backup = parametros['timer_minutos_backup']

                    if ativo:
                        conn = mysql.connector.connect(
                            host="177.153.69.3",
                            user="dinheiro",
                            password="MT49T3.6%B",
                            database="maxservices"
                        )

                        print_log(f"Inicia select das notas - xmlcontador")
                        if sistema_em_uso == '1':  # maxsuport
                            if pasta_compartilhada_backup != '' and \
                                    caminho_base_dados_maxsuport != '' and \
                                    caminho_gbak_firebird_maxsuport != '' and \
                                    porta_firebird_maxsuport != '':
                                ofdb = fdb.load_api(
                                    f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll')
                                con = fdb.connect(
                                    host='localhost',
                                    database=caminho_base_dados_maxsuport,
                                    user='sysdba',
                                    password='masterkey',
                                    port=int(porta_firebird_maxsuport)
                                )

                                cur = con.cursor()
                                cur.execute(
                                    'select n.numero,n.chave,n.data_emissao,n.fkempresa, n.xml, n.situacao from nfe_master n')
                                rows = cur.fetchall()
                                for row in rows:
                                    print(row)

                        elif sistema_em_uso == '2':  # gfil
                            if pasta_compartilhada_backup != '' and \
                                    caminho_base_dados_gfil != '' and \
                                    caminho_gbak_firebird_gfil != '':
                                con = fdb.connect(
                                    host='localhost',
                                    database=caminho_base_dados_gfil,
                                    user='GFILMASTER',
                                    password='b32@m451',
                                    port=int(porta_firebird_gfil)
                                )

                                cur = con.cursor()
                                cur.execute('''SELECT c.NOME ,c."CPF" ,c."CNPJ", d."CNPJ" as cnpj_empresa, DATA_EMIS_NFE,XML,XML_CANCELAM 
                                               FROM CONTABILISTA c 
                                                 LEFT OUTER JOIN DIVERSOS d 
                                                   ON c.FILIAL  = d.FILIAL 
                                                 LEFT OUTER JOIN NFE_MESTRE n 
                                                   ON n.FILIAL  = d.FILIAL 
                                            WHERE n.DATA_EMIS_NFE > dateadd(DAY,-5,CURRENT_DATE)''')
                                rows = cur.fetchall()
                                rows_dict = [
                                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                                for row in rows_dict:
                                    try:
                                        XML = zlib.decompress(row['XML'])
                                    except:
                                        print_log('Nota não existe')
                                    try:
                                        XML_CANCELAM = zlib.decompress(
                                            row['XML_CANCELAM'])
                                    except:
                                        print_log('Nota não existe')

                                    print(XML)
                                    print(XML_CANCELAM)

        except Exception as a:
            # self.logger.error(f"{self._svc_name_} {a}.")
            print(a)


class MaxServices(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaxServices"
    _svc_display_name_ = "MaxServices"
    _svc_description_ = "Monitora uso de sistema e dados"

    def __init__(self, args):
        super().__init__(args)
        self.timer_thread_remoto = threadverificaremoto(23)
        self.timer_thread_backup = threadbackuplocal(1800)  # 1800
        self.timer_thread_alerta_bloqueio = threadalertabloqueio(900)
        self.timer_thread_xml_contador = threadxmlcontador(300)
        self.stop = False
        # Configure o logger
        self.logger = logging.getLogger(self._svc_name_)
        self.logger.setLevel(logging.DEBUG)

        log_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{self._svc_name_}.log")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def SvcStop(self):
        self.timer_thread_remoto.event.set()
        self.timer_thread_backup.event.set()
        self.timer_thread_alerta_bloqueio.event.set()
        self.timer_thread_xml_contador.event.set()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop = True

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.timer_thread_remoto.start()
        self.timer_thread_backup.start()
        self.timer_thread_alerta_bloqueio.start()
        self.timer_thread_xml_contador.start()

        while not self.stop:
            try:
                print_log(f"pega dados local - MaxServices")
                if os.path.exists("C:/Users/Public/config.json"):
                    with open('C:/Users/Public/config.json', 'r') as config_file:
                        config = json.load(config_file)
                    # Ler arquivo INI
                    # Acessar valor
                    for cnpj in config['sistema']:
                        parametros = config['sistema'][cnpj]
                        ativo = parametros['sistema_ativo']
                        sistema_em_uso = parametros['sistema_em_uso_id']
                        caminho_base_dados_gfil = parametros['caminho_base_dados_gfil'].replace(
                            '\\', '/')
                        caminho_base_dados_gfil = caminho_base_dados_gfil.split(
                            '/')[0] + '/' + caminho_base_dados_gfil.split('/')[1]
                        caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
                        caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
                        porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
                        ip = parametros['ip']

                        print_log(
                            f"local valor {ativo} do cnpj {cnpj} - MaxServices")

                        if ativo == "0" and sistema_em_uso == "2":
                            print_log(
                                f"Encerra Processo do GFIL - MaxServices")
                            for proc in psutil.process_iter(['name', 'exe']):
                                if 'FIL' in proc.info['name']:
                                    if caminho_base_dados_gfil in proc.info['exe'].replace('\\', '/'):
                                        print_log(
                                            f"Encerra Processo do GFIL na proc {caminho_base_dados_gfil}, no caminho {proc.info['exe']}- MaxServices")
                                        proc.kill()
                                        print_log(
                                            f"Iniciar conexão com alerta - MaxServices")
                                        exibe_alerta(
                                            "1Sistema bloqueado por inadimplência de mensalidades.\nEntre em contato com o suporte!\n(66) 99926-4708\n(66) 99635-3159\n(66) 99935-3355\n-------------------------------\nAtenciosamente\nMax Suport Sistemas;")

                        if sistema_em_uso == "1":
                            data_cripto = '80E854C4A6929988F97AE2'
                            if ativo == "1":
                                data_cripto = '80E854C4A6929988F879E1'
                            try:
                                con = fdb.connect(
                                    host='localhost',
                                    database=caminho_base_dados_maxsuport,
                                    user='sysdba',
                                    password='masterkey',
                                    port=int(porta_firebird_maxsuport)
                                )
                                comando = 'Liberar'
                                if ativo == "0":
                                    comando = 'Bloquear'
                                print_log(
                                    f"Comando para {comando} maxsuport- MaxServices")

                                cur = con.cursor()
                                cur.execute(
                                    f"UPDATE EMPRESA SET DATA_VALIDADE = '{data_cripto}' WHERE CNPJ = '{cnpj}' ")
                                con.commit()
                                con.close()
                                # if ativo == "0":
                                #    exibe_alerta(
                                #        "1Sistema bloqueado por inadimplência de mensalidades.\nEntre em contato com o suporte!\n(66) 99926-4708\n(66) 99635-3159\n(66) 99935-3355\n-------------------------------\nAtenciosamente\nMax Suport Sistemas;")

                            except fdb.fbcore.DatabaseError as e:
                                # Lidar com a exceção
                                print("Erro ao executar consulta:", e)
            except Exception as a:
                print_log(f"local valor {self._svc_name_} {a} - MaxServices")
            time.sleep(7)


def exibe_alerta(aviso):
    # Envia Alerta
    import socket
    # Configurar as informações do servidor
    host = 'localhost'  # Endereço IP ou nome do host do servidor
    port = 15001  # Porta do servidor

    # Criar um objeto de socket
    client_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)

    # Conectar ao servidor
    client_socket.connect((host, port))
    print_log(f"Conectado com o alerta - MaxServices")
    # Envia comando
    client_socket.send(aviso.encode('utf-8'))

    # Receber a resposta do servidor
    resposta = client_socket.recv(1024).decode('utf-8')
    print_log(f"Resposta do servidor {resposta} - MaxServices")

    # Fechar a conexão
    client_socket.close()


def print_log(texto):
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MaxServices)
