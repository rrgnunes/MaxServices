
import dropbox
from dropbox.exceptions import AuthError
from parametros import *
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from funcoes import select,insert, update
import json


ACCESS_TOKEN = ACCESS_TOKEN_DROP_BOX
REFRESH_TOKEN = REFRESH_TOKEN_DROP_BOX

result_dropbox = select("select * from configuracao_configuracao")
APP_KEY = result_dropbox[0][1]
APP_SECRET = result_dropbox[0][2]

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
    oauth_result_json = json.dumps(oauth_result, indent=2)
    print(oauth_result_json)

except Exception as e:
    print(f"Erro durante a autenticação: {e}")

# with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token,
#                      oauth2_access_token_expiration=oauth_result.expires_at,
#                      oauth2_refresh_token=oauth_result.refresh_token,
#                      app_key=APP_KEY,
#                      app_secret=APP_SECRET) as dbx:
#     dbx.users_get_current_account()
    