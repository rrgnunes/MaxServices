import requests
import json
import time
import parametros
import base64
from PIL import Image, ImageOps
from io import BytesIO
import os

secret_key = 'THISISMYSECURETOKEN'
url = f"https://zap.maxsuportsistemas.com"

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

def close_zap(session):
    headers = {
        "Authorization": f"Bearer {parametros.TOKEN_ZAP}",
        "Content-Type": "application/json"
    }    
    enpoint = f'{url}/api/{session}/logout-session'
    response = requests.post(enpoint, headers=headers)
    enpoint = f'{url}/api/{session}/close-session'
    response = requests.post(enpoint, headers=headers)

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
    
    # print(response)  

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

def add_border_to_image(image, border, color=0):
    """
    Adiciona uma borda ao redor de uma imagem.
    :param image: Imagem PIL.
    :param border: Largura da borda.
    :param color: Cor da borda.
    :return: Imagem PIL com a borda.
    """
    if isinstance(border, int):
        border = (border, border)
    return ImageOps.expand(image, border=border, fill=color)

def gera_qrcode(data_qrcode):
    # Decodifica o QR Code de Base64 para dados de imagem
    qr_img_data = base64.b64decode(data_qrcode)
    if parametros.LAST_IMAGE != data_qrcode:
       parametros.LAST_IMAGE = data_qrcode
       os.remove("c:\maxsuport\qr_code_with_border.png")
    # Cria uma imagem a partir dos dados decodificados
    image = Image.open(BytesIO(qr_img_data))
    # Adiciona uma borda à imagem
    bordered_image = add_border_to_image(image, border=10, color='white')
    # Salva a imagem com borda
    bordered_image.save("c:\maxsuport\qr_code_with_border.png")

def qrcode_session(session):
    enpoint = f'{url}/api/{session}/qrcode-session'
    headers = {
        "accept": "*/*",
        "Authorization": "Bearer " + parametros.TOKEN_ZAP
    }
    response = requests.get(enpoint, headers=headers)
    print(response.text)