import sys
from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox.exceptions import AuthError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais.parametros import *
from funcoes.funcoes import select, update


ACCESS_TOKEN = ACCESS_TOKEN_DROP_BOX
REFRESH_TOKEN = REFRESH_TOKEN_DROP_BOX

result_dropbox = select("select * from configuracao_configuracao")[0]
APP_KEY = result_dropbox['app_key_drop_box']
APP_SECRET = result_dropbox['app_secret_drop_box']
ACCESS_TOKEN = result_dropbox['access_token_drop_box']

auth_flow3 = DropboxOAuth2FlowNoRedirect(consumer_key=APP_KEY,
                                         consumer_secret=APP_SECRET,
                                         token_access_type='offline',
                                         scope=['files.content.read', 'files.content.write'],
                                         include_granted_scopes='user')

authorize_url = auth_flow3.start()
print("1. Entre neste site: " + authorize_url)
print("2. Clique em permitir")
print("3. Copie o código de autorização")
auth_code = input("Cole o código aqui: ").strip()

try:
    oauth_result = auth_flow3.finish(auth_code)
    
    sql = '''update configuracao_configuracao set access_token_drop_box = %s,
                                                  refresh_token_drop_box = %s,
                                                  account_id_drop_box = %s,
                                                  expira_em = %s,
                                                  user_id_drop_box = %s'''

    update(sql,(oauth_result.access_token,oauth_result.refresh_token,oauth_result.account_id,oauth_result.expires_at,oauth_result.user_id))
    print("Tudo finalizado papito")
except Exception as e:
    print(f"Erro durante a autenticação: {e}")

# with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token,
#                      oauth2_access_token_expiration=oauth_result.expires_at,
#                      oauth2_refresh_token=oauth_result.refresh_token,
#                      app_key=APP_KEY,
#                      app_secret=APP_SECRET) as dbx:
#     dbx.users_get_current_account()
    