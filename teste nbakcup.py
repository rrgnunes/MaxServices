import win32serviceutil
import win32service
import servicemanager
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
			
def print_log(texto):
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d_%m_%Y_%H_%M_%S')
    logger.info(texto)
    print(f'{texto} - {data_hora_formatada}')			