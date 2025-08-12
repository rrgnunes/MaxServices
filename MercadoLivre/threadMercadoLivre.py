import sys
import os
import json
import meli
from meli.rest import ApiException

# Adiciona a pasta pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','funcoes')))
from funcoes import (
    print_log, criar_bloqueio, remover_bloqueio,
    pode_executar, selectfb, updatefb,
    carregar_configuracoes, inicializa_conexao_firebird
)

HOMOLOGACAO = True  # Modo homologação

CLIENT_ID = '1419823096250136'
CLIENT_SECRET = 'LHrlkAhTksa2usHBtykgrt3jVUv5r9rR'
REDIRECT_URI = 'https://maxsuport.com/'
AUTH_HOST = "https://auth.mercadolivre.com.br"

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token_meli.json')
TEST_USER_FILE = os.path.join(os.path.dirname(__file__), 'test_user.json')

# ========================= TOKENS ==========================

def salvar_token(data):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def carregar_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return {}

def gerar_token(api_oauth, code):
    api_response = api_oauth.get_token(
        grant_type='authorization_code',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        code=code
    )
    return {
        'code': code,
        'access_token': api_response['access_token'],
        'refresh_token': api_response['refresh_token']
    }

def refresh_token(api_oauth, refresh_token):
    api_response = api_oauth.get_token(
        grant_type='refresh_token',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=refresh_token
    )
    return {
        'access_token': api_response['access_token'],
        'refresh_token': api_response['refresh_token']
    }

# ========================= TEST USER ==========================

def criar_usuario_teste_ml():
    nome_servico = 'thread_criar_usuario_teste_ml'
    tokens = carregar_token()

    if 'access_token' not in tokens:
        print_log("Gerando token para criar usuário de teste...", nome_servico)
        return None

    configuration = meli.Configuration(host="https://api.mercadolibre.com")
    with meli.ApiClient(configuration) as api_client:
        api_instance = meli.RestClientApi(api_client)
        body = {"site_id": "MLB"}
        api_response = api_instance.resource_post('users/test_user', tokens['access_token'], body)

        with open(TEST_USER_FILE, 'w') as f:
            json.dump(api_response, f, indent=4)
        print_log(f"Usuário de teste criado: {api_response}", nome_servico)
        return api_response

def carregar_usuario_teste():
    if os.path.exists(TEST_USER_FILE):
        with open(TEST_USER_FILE, 'r') as f:
            return json.load(f)
    return None

def gerar_token_usuario_teste():
    nome_servico = 'thread_gerar_token_teste'
    user_test = carregar_usuario_teste()
    if not user_test:
        user_test = criar_usuario_teste_ml()
        if not user_test:
            return

    print_log(f"Use este login para gerar o CODE: {user_test['nickname']} / {user_test['password']}", nome_servico)
    auth_url = f"{AUTH_HOST}/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    print_log(f"Acesse: {auth_url}", nome_servico)

    code = input("Cole aqui o CODE recebido no callback: ").strip()

    configuration = meli.Configuration(host="https://api.mercadolibre.com")
    with meli.ApiClient(configuration) as api_client:
        api_oauth = meli.OAuth20Api(api_client)
        api_response = api_oauth.get_token(
            grant_type='authorization_code',
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            code=code
        )
        tokens = {
            'code': code,
            'access_token': api_response['access_token'],
            'refresh_token': api_response['refresh_token']
        }
        salvar_token(tokens)
        print_log("Token do usuário de teste salvo em token_meli.json", nome_servico)

# ========================= ATUALIZA TOKEN ==========================

def atualiza_mercadolivre():
    nome_servico = 'thread_atualiza_mercadolivre'
    configuration = meli.Configuration(host="https://api.mercadolibre.com")

    with meli.ApiClient(configuration) as api_client:
        api_oauth = meli.OAuth20Api(api_client)
        tokens = carregar_token()

        if 'access_token' not in tokens:
            if HOMOLOGACAO:
                print_log("Modo homologação ativo: criando usuário e token...", nome_servico)
                criar_usuario_teste_ml()
                gerar_token_usuario_teste()
                tokens = carregar_token()
            else:
                auth_url = f"{AUTH_HOST}/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
                print_log(f"Acesse para autorizar: {auth_url}", nome_servico)
                code = input("Cole aqui o CODE recebido no callback: ").strip()
                tokens = gerar_token(api_oauth, code)
                salvar_token(tokens)

        access_token = tokens['access_token']
        refresh = tokens.get('refresh_token', '')

        try:
            api_rest = meli.RestClientApi(api_client)
            response_user = api_rest.resource_get('users/me', access_token)
            print_log(f"Dados do usuário: {response_user}", nome_servico)
        except ApiException:
            if refresh:
                print_log("Access token expirado, renovando...", nome_servico)
                new_tokens = refresh_token(api_oauth, refresh)
                tokens.update(new_tokens)
                salvar_token(tokens)

# ========================= ENVIO PRODUTOS ==========================

def enviar_produtos_ml():
    tokens = carregar_token()
    access_token = tokens.get('access_token')

    if not access_token:
        print_log("Access token não encontrado. Rode atualiza_mercadolivre primeiro.", "MercadoLivre")
        return

    # if HOMOLOGACAO:
    #     if not carregar_usuario_teste():
    #         criar_usuario_teste_ml()
    #     gerar_token_usuario_teste()
    #     tokens = carregar_token()
    #     access_token = tokens.get('access_token')

    configuration = meli.Configuration(host="https://api.mercadolibre.com")
    with meli.ApiClient(configuration) as api_client:
        api_instance = meli.RestClientApi(api_client)

        try:
            response_user = api_instance.resource_get('users/me', access_token)
            print_log(f"Usuário autenticado (token): {response_user}", "MercadoLivre")
        except ApiException as e:
            print_log(f"Erro ao validar usuário: {e}", "MercadoLivre")
            return

        produtos = selectfb(
            """
            SELECT CODIGO, DESCRICAO, PR_VENDA, PE.ESTOQUE_ATUAL, CODIGO_ML
            FROM PRODUTO PR
            LEFT OUTER JOIN PRODUTO_ESTOQUE PE
              ON PR.CODIGO = PE.PRODUTO
            WHERE ENVIA_ML = 1
            """,
            []
        )

        if not produtos:
            print_log("Nenhum produto para enviar ao Mercado Livre", "MercadoLivre")
            return

        for produto in produtos:
            codigo, descricao, preco, quantidade, codigo_ml = produto

            body = {
                "site_id": "MLB",
                "title": "Item de Teste - Por favor, NÃO OFERTAR!" if HOMOLOGACAO else descricao[:60],
                "category_id": "MLB3530",
                "price": str(preco),
                "currency_id": "BRL",
                "available_quantity": str(int(quantidade)),
                "buying_mode": "buy_it_now",
                "listing_type_id": "bronze",
                "condition": "new",
                "description": descricao[:1000],
                "attributes": [
                    { "id": "BRAND", "value_name": "ACME" },
                    { "id": "MODEL", "value_name": "X200" }
                ],
                "pictures": [
                    { "source": "https://maxsuport.com/img/logo.webp" }
                ]                
            }

            try:
                if codigo_ml:
                    body = { "available_quantity": str(int(quantidade)),
                             "price": str(preco)
                           }
                    api_response = api_instance.resource_put(f'items/{codigo_ml}', access_token, body)
                else:
                    api_response = api_instance.resource_post('items', access_token, body)
                codigo_ml = api_response['id']
                perman_link = api_response['permalink']
                updatefb("UPDATE PRODUTO SET CODIGO_ML = ?, ANUNCIO_ML=? WHERE CODIGO = ?", [codigo_ml, perman_link, codigo])
                print_log(f"Produto {codigo} enviado ao Mercado Livre -> {codigo_ml}", "MercadoLivre")
            except ApiException as e:
                print_log(f"Erro ao enviar produto {codigo}: {e}", "MercadoLivre")

# ========================= MAIN ==========================

if __name__ == '__main__':
    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            carregar_configuracoes()
            inicializa_conexao_firebird()
            atualiza_mercadolivre()
            enviar_produtos_ml()
        except Exception as e:
            print_log(f"Ocorreu um erro na execução - motivo: {e}", nome_script)
        finally:
            remover_bloqueio(nome_script)
