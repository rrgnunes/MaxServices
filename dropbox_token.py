
import dropbox
from dropbox.exceptions import AuthError
from parametros import *
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY = APP_KEY_DROP_BOX
APP_SECRET = APP_SECRET_DROP_BOX
ACCESS_TOKEN = ACCESS_TOKEN_DROP_BOX
REFRESH_TOKEN = REFRESH_TOKEN_DROP_BOX

auth_flow3 = DropboxOAuth2FlowNoRedirect(APP_KEY,
                                         consumer_secret=APP_SECRET,
                                         token_access_type='legacy',
                                         scope=['files.content.read', 'files.content.write'],
                                         include_granted_scopes='user')

authorize_url = auth_flow3.start()
print("1. Go to: " + authorize_url)
print("2. Click \"Allow\" (you might have to log in first).")
print("3. Copy the authorization code.")
auth_code = input("Enter the authorization code here: ").strip()

try:
    oauth_result = auth_flow3.finish(auth_code)
    print(oauth_result)
    print("Successfully set up client!")
except Exception as e:
    print('Error: %s' % (e,))
    exit(1)

# with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token,
#                      oauth2_access_token_expiration=oauth_result.expires_at,
#                      oauth2_refresh_token=oauth_result.refresh_token,
#                      app_key=APP_KEY,
#                      app_secret=APP_SECRET) as dbx:
#     dbx.users_get_current_account()
    