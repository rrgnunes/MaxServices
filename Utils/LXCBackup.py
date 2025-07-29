import os
import sys
import glob
import dropbox
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dropbox.files import WriteMode
from datetime import datetime
from funcoes.funcoes import select, update

# Configurações
BACKUP_DIR = "/caminho/para/backup"
DROPBOX_DIR = "/ServidorLXC"
NUM_BACKUPS = 500

# Configurações do Dropbox
configuracao = select("select * from configuracao_configuracao")[0]
ACCESS_TOKEN_DROP_BOX = configuracao['access_token_drop_box']
REFRESH_TOKEN_DROP_BOX = configuracao['refresh_token_drop_box']
APP_KEY_DROP_BOX = configuracao['app_key_drop_box']
APP_SECRET_DROP_BOX = configuracao['app_secret_drop_box']

# Conectar ao Dropbox
dbx = dropbox.Dropbox(
    oauth2_access_token=ACCESS_TOKEN_DROP_BOX,
    oauth2_refresh_token=REFRESH_TOKEN_DROP_BOX,
    app_key=APP_KEY_DROP_BOX,
    app_secret=APP_SECRET_DROP_BOX
)
dbx.check_and_refresh_access_token()

# Atualiza tokens
sql = '''update configuracao_configuracao set access_token_drop_box = %s, refresh_token_drop_box = %s'''
update(sql, (dbx._oauth2_access_token, dbx._oauth2_refresh_token))

# Obtém lista de containers LXC
containers = subprocess.check_output("lxc list --format=json", shell=True)
containers = eval(containers)  # Converte JSON para lista

# Faz backup de cada container
for container in containers:
    nome_container = container["name"]
    pasta_local = os.path.join(BACKUP_DIR, nome_container)
    os.makedirs(pasta_local, exist_ok=True)

    # Nome do arquivo de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(pasta_local, f"{nome_container}_{timestamp}.tar.xz")

    # Comando para criar backup
    cmd = f"lxc export {nome_container} {backup_file}"
    subprocess.run(cmd, shell=True)

    # Enviar para Dropbox
    dropbox_pasta_container = f"{DROPBOX_DIR}/{nome_container}"
    
    # Cria a pasta no Dropbox se não existir
    try:
        dbx.files_get_metadata(dropbox_pasta_container)
    except dropbox.exceptions.ApiError:
        dbx.files_create_folder_v2(dropbox_pasta_container)

    # Caminho remoto no Dropbox
    dropbox_file = f"{dropbox_pasta_container}/{os.path.basename(backup_file)}"
    
    # Upload do arquivo
    with open(backup_file, "rb") as f:
        dbx.files_upload(f.read(), dropbox_file, mode=WriteMode("overwrite"))

    print(f"Backup de {nome_container} enviado para {dropbox_file}")

    # Remover backups antigos locais
    arquivos = sorted(glob.glob(os.path.join(pasta_local, "*.tar.xz")), key=os.path.getmtime)
    if len(arquivos) > NUM_BACKUPS:
        for arq in arquivos[:len(arquivos) - NUM_BACKUPS]:
            os.remove(arq)
            print(f"Arquivo removido localmente: {arq}")

print("Backup concluído!")
dbx.close()