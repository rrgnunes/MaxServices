import requests
import json
import time
import parametros

secret_key = 'ERTYHN^dsdasfds484D^d^'
url = f"http://91.108.126.27:8081"

def retorna_json(resposta):
    response_dict = json.loads(resposta.text)
    return response_dict

def generate_token(session):
    enpoint = f'{url}/api/{session}/{secret_key}/generate-token'
    headers = {
        "accept": "*/*"
    }

    response = requests.post(enpoint, headers=headers)
    response = retorna_json(response)
    return response

def start_session(session):
    enpoint = f'{url}/api/{session}/start-session'
    tudo_ok = False
    while not tudo_ok:
        headers = {
            "accept": "*/*",
            "Authorization": "Bearer " + parametros.TOKEN_ZAP
        }

        payload = {
        "webhook": "",
        "waitQrCode": True
        }

        response = requests.post(enpoint, headers=headers, data=payload)
        response = retorna_json(response)    
        time.sleep(5)
        print(response['status'])

        if response['status'] == 'QRCODE' or response['status'] == 'CONNECTED':
            tudo_ok = True
    return response  

def start_session(session):
    enpoint = f'{url}/api/{session}/start-session'
    tudo_ok = False
    headers = {
        "accept": "*/*",
        "Authorization": "Bearer " + parametros.TOKEN_ZAP
    }

    payload = {
        "webhook": "",
        "waitQrCode": False
    }

    response = requests.post(enpoint, headers=headers, data=payload)
    response = retorna_json(response)

    if response['status'] == 'CONNECTED':
        tudo_ok = True

    return tudo_ok  

def status_session(session):
    enpoint = f'{url}/api/{session}/status-session'
    tudo_ok = False

    headers = {
        "accept": "*/*",
        "Authorization": "Bearer " + parametros.TOKEN_ZAP
    }

    response = requests.get(enpoint, headers=headers)
    response = retorna_json(response)    

    if response['status'] == 'CLOSED':
        tudo_ok = start_session(session)
    elif response['status'] == 'CONNECTED':
        tudo_ok = True

    return tudo_ok  


def envia_mensagem_zap(session, numero, mensagem):
    enpoint = f'{url}/api/{session}/send-message'
    payload = json.dumps({
        "phone": '55' + numero,
        "message": mensagem,
        "isGroup": False
    })
    headers = {
        "Authorization": f"Bearer {parametros.TOKEN_ZAP}",
        "Content-Type": "application/json"
    }

    response = requests.post(enpoint, headers=headers, data=payload)

    response = retorna_json(response)    

    return response

def receber_mensagem(session):
    enpoint = f'{url}/api/{session}/all-chats'

    headers = {
        "Authorization": f"Bearer {parametros.TOKEN_ZAP}",
        "Content-Type": "application/json"
    }

    response = requests.get(enpoint, headers=headers)
    response = retorna_json(response)       
    return response 
