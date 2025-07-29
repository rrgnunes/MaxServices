import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from credenciais import parametros
from funcoes import carregar_configuracoes, inicializa_conexao_mysql, print_log

def extrair_numeros_telefone(arquivo_entrada, arquivo_saida):
    # Expressão regular para capturar números de telefone após "Enviando para o número"
    padrao = re.compile(r"Enviando para o número (\d+)")
    
    # Lista para armazenar números únicos
    numeros = set()

    # Ler o arquivo de entrada e extrair os números
    with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            match = padrao.search(linha)
            if match:
                numeros.add(match.group(1))

    # Salvar os números extraídos no arquivo de saída
    with open(arquivo_saida, 'w', encoding='utf-8') as saida:
        for numero in sorted(numeros):
            saida.write(numero + '\n')

    print(f"Extração concluída! {len(numeros)} números salvos em '{arquivo_saida}'.")
    
def atualizar_campanha(caminho_arquivo):
    # Configuração inicial
    parametros.BASEMYSQL = 'maxservices'
    carregar_configuracoes()
    inicializa_conexao_mysql()

    nome_servico = 'Campanha ZAP'
    print_log("Iniciando atualização de campanha", nome_servico)

    # Verifica se o arquivo existe
    if not os.path.isfile(caminho_arquivo):
        print_log(f"Arquivo não encontrado: {caminho_arquivo}", nome_servico)
        return

    # Ler os números do arquivo
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        numeros = [linha.strip() for linha in arquivo.readlines() if linha.strip()]

    if not numeros:
        print_log("Nenhum número encontrado no arquivo.", nome_servico)
        return

    # Atualizar os registros no banco de dados
    cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)

    try:
        placeholders = ', '.join(['%s'] * len(numeros))
        query = f'''
            UPDATE cliente_lead 
            SET campanha_enviado = 1 
            WHERE campanha_enviado IS NULL 
            AND REPLACE(SUBSTRING_INDEX(telefone, ' ', 2), ' ', '') IN ({placeholders})
        '''
        cur_con.execute(query, numeros)
        parametros.MYSQL_CONNECTION.commit()

        print_log(f"{cur_con.rowcount} registros atualizados com sucesso.", nome_servico)

    except Exception as e:
        print_log(f"Erro ao atualizar os registros: {e}", nome_servico)

    finally:
        cur_con.close()

# Chamar a função com o arquivo de números
atualizar_campanha('/home/MaxServices/log/numeros_extraidos.txt')    

# Uso do script
#extrair_numeros_telefone('/home/MaxServices/log/numero_ja_enviados.txt', '/home/MaxServices/log/numeros_extraidos.txt')