import requests

def envia_audio_texto_api_comando():        
    url = "http://10.105.96.102:8000/processar_audio/"
    
    with open('/home/MaxServices/teste/erivelton.mp3', "rb") as f:
        files = {"arquivo": ("audio.wav", f, "audio/wav")}
        data = {"cnpj_empresa": 1}  # Adiciona o CNPJ no envio
        response = requests.post(url, files=files, data=data)

    print("📨 Resposta da API:", response.text)
    
    return response.text   

texto = envia_audio_texto_api_comando()
print(texto)