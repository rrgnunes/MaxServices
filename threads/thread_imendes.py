import requests
import datetime

def consultar_regras_fiscais():
    # Credenciais fornecidas
    sLogin = "19775656000104"
    sSenha = "QsuS21Pd3dtI"

    # URL
    sUrl = "https://consultatributos.com.br:8443/api/v2/public/RegrasFiscais"

    # Headers obrigatórios
    oHeaders = {
        "Login": sLogin,
        "Senha": sSenha,
        "Content-Type": "application/json"
    }

    # JSON de envio com env na raiz
    oPayload = {
        "env": 1,  # 1 = Homologação, 2 = Produção
        "cabecalho": {
            "cnpj": sLogin,
            "cnae": "4711302",
            "cnaeSecundario": "1091102",
            "fabricacaoPropria": True,
            "crt": 3,
            "regimeEspecial": "",
            "codFaixa": 99,
            "amb": 1,
            "municipio": "3550308",
            "dia": datetime.datetime.now().day,
            "mes": datetime.datetime.now().month,
            "ano": datetime.datetime.now().year,
            "dthr": datetime.datetime.now().isoformat(),
            "prodEnv": 1,
            "prodRet": 0,
            "transacao": "Teste001",
            "mensagem": "Consulta em homologação",
            "aces_primeiro": "",
            "aces_expirar": "",
            "versao": "3.43",
            "regimeTrib": "R",
            "contribuinte": 1
            # "duracao": "00:00:30"  # só se quiser preencher, senão omite
        },
        "uf": ["MT"],
        "produto": [
            {
                "codigo": "7894900010015",
                "codIMendes": "",
                "descricao": "Refrigerante Cola 2L",
                "ncm": "22021000",
                "cest": "0300700",
                "tipoCodigo": 0,
                "refeicao": "N",
                "encontrado": True
            }
        ]
    }

    try:
        oResp = requests.post(
            sUrl,
            headers=oHeaders,
            json=oPayload,
            timeout=60
        )
        oResp.raise_for_status()
        return oResp.json()
    except Exception as e:
        return {"erro": str(e)}

# Exemplo de uso
if __name__ == "__main__":
    print(consultar_regras_fiscais())