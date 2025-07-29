import requests

# Variáveis de configuração
client_id = 'tiny-api-95ceb802071151089862532d9ac6482e7316a852-1722287903'
client_secret = 'SaRHkI9AtXDL8kCsWYN79iEsfnACdezx'
redirect_uri = 'https://www.google.com.br/' 
access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJnWXk2cDhkQkU0dDBkZkFvU0J4WkJvbDBkYmpTcEF5Z3FpQm1vY3pMcXJVIn0.eyJleHAiOjE3MjQ4NjYzNjUsImlhdCI6MTcyNDg1MTk2NSwiYXV0aF90aW1lIjoxNzIzODEyMjQ2LCJqdGkiOiI0OTA3ZWUxMi0wYWRmLTQzZTktOTY5OC1hNWM4N2EwZWUzZjciLCJpc3MiOiJodHRwczovL2FjY291bnRzLnRpbnkuY29tLmJyL3JlYWxtcy90aW55IiwiYXVkIjoidGlueS1hcGkiLCJzdWIiOiI2MjUwNmZhYS1lMjY0LTQwYjktYjYzYi0yMzcyMTZlYjFlMTQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0aW55LWFwaS05NWNlYjgwMjA3MTE1MTA4OTg2MjUzMmQ5YWM2NDgyZTczMTZhODUyLTE3MjIyODc5MDMiLCJzZXNzaW9uX3N0YXRlIjoiNmQ2ZmU4N2EtODkzZi00NzBlLTkxMjMtODhhMmM5ZWRjNGMxIiwic2NvcGUiOiJvcGVuaWQgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJzaWQiOiI2ZDZmZTg3YS04OTNmLTQ3MGUtOTEyMy04OGEyYzllZGM0YzEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInJvbGVzIjp7InRpbnktYXBpIjpbIm1hcmNhcy1lc2NyaXRhIiwicGVkaWRvcy1sZWl0dXJhIiwiZXN0b3F1ZS1sZWl0dXJhIiwibm90YXMtZmlzY2Fpcy1lc2NyaXRhIiwiY29udGF0b3MtZXhjbHVzYW8iLCJpbmZvLWNvbnRhLWxlaXR1cmEiLCJwcm9kdXRvcy1leGNsdXNhbyIsImxpc3RhLXByZWNvcy1sZWl0dXJhIiwiY2F0ZWdvcmlhcy1sZWl0dXJhIiwiZXhwZWRpY2FvLWV4Y2x1c2FvIiwiZm9ybWEtZW52aW8tbGVpdHVyYSIsInNlcGFyYWNhby1sZWl0dXJhIiwicHJvZHV0b3MtbGVpdHVyYSIsImV4cGVkaWNhby1sZWl0dXJhIiwibm90YXMtZmlzY2Fpcy1sZWl0dXJhIiwiY29udGF0b3MtZXNjcml0YSIsInBlZGlkb3MtZXNjcml0YSIsImV4cGVkaWNhby1lc2NyaXRhIiwic2VwYXJhY2FvLWVzY3JpdGEiLCJtYXJjYXMtbGVpdHVyYSIsImZvcm1hLXBhZ2FtZW50by1sZWl0dXJhIiwiaW50ZXJtZWRpYWRvcmVzLWxlaXR1cmEiLCJnYXRpbGhvcyIsImVzdG9xdWUtZXNjcml0YSIsInByb2R1dG9zLWVzY3JpdGEiLCJwZWRpZG9zLWV4Y2x1c2FvIiwiY29udGF0b3MtbGVpdHVyYSIsIm5vdGFzLWZpc2NhaXMtZXhjbHVzYW8iXX0sImVtYWlsIjoiZGlvZ29AY2FzYWRvbWVkaWNvLmNvbS5iciJ9.MGf8dmYn8DBgjEVV1fibA3sseR0_OLlAm-MVQjSt07c1SZU4FVCUxAc_p9LkHaANpX5RnDDtN7Uimvb21BujTsm9mupPGvxdmu79v_7pSz8p1x7MMbv5b95irBZ9wQxmyseF8tyVi4meZFoKvezxey-UnTyZ06YqQi1FFUybmukqA46_PX28te2RmsBi7ROjfWyR4PaAUUpq0o3Tuo4jMc2itMMxBtkcZa1WK2BKPKqyUSAVwjqGK7HYdEO3RpgVTFPsCGLxI7rwEpTsFEv2vuE3s71tECnG759_-Po7MzHv9Q6I0sgKbQMK8fmoh95jD0tf1zy4z6TkSl4kqlc-gQ'
refresh_token = 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI5MDNkY2IxNi0xNTgwLTQ0NzYtYWY0Mi1lYTFkN2YyNzY4MjcifQ.eyJleHAiOjE3MjQ5MzgzNjUsImlhdCI6MTcyNDg1MTk2NSwianRpIjoiMDUwMDdhZWUtN2RlOC00MmIxLThjYmMtZDUyZmI3MmUzNjQ3IiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy50aW55LmNvbS5ici9yZWFsbXMvdGlueSIsImF1ZCI6Imh0dHBzOi8vYWNjb3VudHMudGlueS5jb20uYnIvcmVhbG1zL3RpbnkiLCJzdWIiOiI2MjUwNmZhYS1lMjY0LTQwYjktYjYzYi0yMzcyMTZlYjFlMTQiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoidGlueS1hcGktOTVjZWI4MDIwNzExNTEwODk4NjI1MzJkOWFjNjQ4MmU3MzE2YTg1Mi0xNzIyMjg3OTAzIiwic2Vzc2lvbl9zdGF0ZSI6IjZkNmZlODdhLTg5M2YtNDcwZS05MTIzLTg4YTJjOWVkYzRjMSIsInNjb3BlIjoib3BlbmlkIGVtYWlsIG9mZmxpbmVfYWNjZXNzIiwic2lkIjoiNmQ2ZmU4N2EtODkzZi00NzBlLTkxMjMtODhhMmM5ZWRjNGMxIn0.N44NBpk8Bihalb4rHOlYWqojajVK4J3hb_h9vhPgC_Q'

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



# Chama a função nfs para realizar a chamada à API
if access_token:
    separacao(access_token)

# Caso o token expire, renova o token e chama a API novamente
access_token, refresh_token = atualizar_access_token(refresh_token)
if access_token:
    separacao(access_token)
