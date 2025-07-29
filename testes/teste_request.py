import requests

# Variáveis de configuração
client_id = 'tiny-api-95ceb802071151089862532d9ac6482e7316a852-1723813172'
client_secret = 'WpevCE56nQxuOVdPQJj6aww0OvD3u3Ln'
redirect_uri = 'https://erp.tiny.com.br/' 
authorization_code = 'c6666379-0d8f-4088-8185-de4c9e074771.d8764d4b-4ed4-449b-a296-9d107a0549fe.69dc3cc1-4c34-4182-ae93-22494a82ec50' 
access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJnWXk2cDhkQkU0dDBkZkFvU0J4WkJvbDBkYmpTcEF5Z3FpQm1vY3pMcXJVIn0.eyJleHAiOjE3MjQ4ODU1NDAsImlhdCI6MTcyNDg3MTE0MCwiYXV0aF90aW1lIjoxNzI0ODU2MzAwLCJqdGkiOiI1NmIwNTU1Ni1mOWJkLTQ1ZDItODk3Yi1iZTNlMWQzNjc1NGMiLCJpc3MiOiJodHRwczovL2FjY291bnRzLnRpbnkuY29tLmJyL3JlYWxtcy90aW55IiwiYXVkIjoidGlueS1hcGkiLCJzdWIiOiI2MjUwNmZhYS1lMjY0LTQwYjktYjYzYi0yMzcyMTZlYjFlMTQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0aW55LWFwaS05NWNlYjgwMjA3MTE1MTA4OTg2MjUzMmQ5YWM2NDgyZTczMTZhODUyLTE3MjM4MTMxNzIiLCJzZXNzaW9uX3N0YXRlIjoiZDg3NjRkNGItNGVkNC00NDliLWEyOTYtOWQxMDdhMDU0OWZlIiwic2NvcGUiOiJvcGVuaWQgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJzaWQiOiJkODc2NGQ0Yi00ZWQ0LTQ0OWItYTI5Ni05ZDEwN2EwNTQ5ZmUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInJvbGVzIjp7InRpbnktYXBpIjpbIm1hcmNhcy1lc2NyaXRhIiwiZXN0b3F1ZS1sZWl0dXJhIiwicGVkaWRvcy1sZWl0dXJhIiwibm90YXMtZmlzY2Fpcy1lc2NyaXRhIiwiY29udGF0b3MtZXhjbHVzYW8iLCJpbmZvLWNvbnRhLWxlaXR1cmEiLCJsaXN0YS1wcmVjb3MtbGVpdHVyYSIsInByb2R1dG9zLWV4Y2x1c2FvIiwiY2F0ZWdvcmlhcy1sZWl0dXJhIiwiZXhwZWRpY2FvLWV4Y2x1c2FvIiwic2VwYXJhY2FvLWxlaXR1cmEiLCJmb3JtYS1lbnZpby1sZWl0dXJhIiwicHJvZHV0b3MtbGVpdHVyYSIsImV4cGVkaWNhby1sZWl0dXJhIiwiY29udGF0b3MtZXNjcml0YSIsIm5vdGFzLWZpc2NhaXMtbGVpdHVyYSIsInBlZGlkb3MtZXNjcml0YSIsImV4cGVkaWNhby1lc2NyaXRhIiwic2VwYXJhY2FvLWVzY3JpdGEiLCJtYXJjYXMtbGVpdHVyYSIsImZvcm1hLXBhZ2FtZW50by1sZWl0dXJhIiwiaW50ZXJtZWRpYWRvcmVzLWxlaXR1cmEiLCJnYXRpbGhvcyIsImVzdG9xdWUtZXNjcml0YSIsInByb2R1dG9zLWVzY3JpdGEiLCJjb250YXRvcy1sZWl0dXJhIiwicGVkaWRvcy1leGNsdXNhbyIsIm5vdGFzLWZpc2NhaXMtZXhjbHVzYW8iXX0sImVtYWlsIjoiZGlvZ29AY2FzYWRvbWVkaWNvLmNvbS5iciJ9.PDHrkFDCk2MyTKFe36punCQ6LH3huskqbf_IQsfvJKjrI-9_AS0qSupATMGT7y4fszkthIFJVEN-XrkHhQYb4YeHDry5xHMXOSHNLAb_gttGiYZW-y3v7kP5SdfxtsL-tu-MQly6ytYPb0RFL9Xto7Bc2f_EIKgfIUnc5mCNkYa8YvVB0MxLm3GvixDOse3k-vTYtLucbyEbzfkUXNYB0pWRdDzvfXKYd-CZDxtFSQ76MZt7QGd34VX1qY1MS4TO6X3J_64UnamT19wu-zP38T0xbXqTMcnQwxoqega1_HjtDDBbdlsec01iVPca1000AZyM4G_WyPRgDI2dkIiw'
refresh_token = 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI5MDNkY2IxNi0xNTgwLTQ0NzYtYWY0Mi1lYTFkN2YyNzY4MjcifQ.eyJleHAiOjE3MjQ5NTc1NDAsImlhdCI6MTcyNDg3MTE0MCwianRpIjoiOGI0MWZlZGQtOTA1OS00NjRjLTg3NzUtZjg2OWVjY2NlYjU2IiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy50aW55LmNvbS5ici9yZWFsbXMvdGlueSIsImF1ZCI6Imh0dHBzOi8vYWNjb3VudHMudGlueS5jb20uYnIvcmVhbG1zL3RpbnkiLCJzdWIiOiI2MjUwNmZhYS1lMjY0LTQwYjktYjYzYi0yMzcyMTZlYjFlMTQiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoidGlueS1hcGktOTVjZWI4MDIwNzExNTEwODk4NjI1MzJkOWFjNjQ4MmU3MzE2YTg1Mi0xNzIzODEzMTcyIiwic2Vzc2lvbl9zdGF0ZSI6ImQ4NzY0ZDRiLTRlZDQtNDQ5Yi1hMjk2LTlkMTA3YTA1NDlmZSIsInNjb3BlIjoib3BlbmlkIGVtYWlsIG9mZmxpbmVfYWNjZXNzIiwic2lkIjoiZDg3NjRkNGItNGVkNC00NDliLWEyOTYtOWQxMDdhMDU0OWZlIn0.1bXApKQx5z9DldPBddvrSaILAL1ywYVpkCfZAEE9u5o'

# Solicitação do token de acesso inicial
def solicitar_token_inicial():
    url = 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code  
    }

    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()
    print(response_data)

    return response_data.get('access_token'), response_data.get('refresh_token')

# Solicitação de refresh token para obter um novo access_token
def solicitar_refresh_token(refresh_token):
    url = 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }

    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()
    print(response_data)

    return response_data.get('access_token'), response_data.get('refresh_token')

# Função para atualizar o access_token
def atualizar_access_token(refresh_token):
    return solicitar_refresh_token(refresh_token)

# Função para chamar a API de notas fiscais
def separacao(access_token):
    url = 'https://api.tiny.com.br/public-api/v3/separacao'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(response.text)
    else:
        print(f'Erro {response.status_code}: {response.text}')

# Passo inicial: Obtenção do código de autorização
authorization_url = f"https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope=openid&response_type=code"
print("Por favor, acesse a seguinte URL, autorize o aplicativo e obtenha o código de autorização:")
print(authorization_url)

# Depois de obter o código de autorização, defina-o na variável authorization_code e execute o restante do script
if authorization_code:
    # # Solicita o token inicial usando o código de autorização
    if not access_token:
        access_token, refresh_token = solicitar_token_inicial()

    # # Chama a função nfs para realizar a chamada à API
    # if access_token:
    #     separacao(access_token)
    
    # Caso o token expire, renova o token e chama a API novamente
    access_token, refresh_token = atualizar_access_token(refresh_token)
    if access_token:
        separacao(access_token)
else:
    print("Defina o código de autorização na variável 'authorization_code' antes de prosseguir.")
