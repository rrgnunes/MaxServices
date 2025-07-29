from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def consulta_produto_ean(ean):
    url = f"https://cosmos.bluesoft.com.br/produtos/{ean}"
    
    # Configura o webdriver para usar o Chrome em modo headless
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executa o navegador em modo headless (sem interface gráfica)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Inicializa o webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    try:
        # Espera pelo desaparecimento do overlay do Cloudflare
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.ID, "challenge-running"))
        )

        # Aguarda a página carregar completamente após passar pela proteção do Cloudflare
        time.sleep(5)  # Ajuste o tempo de espera conforme necessário

        # Extrair NCM
        ncm_element = driver.find_element(By.XPATH, "//strong[text()='NCM:']/following-sibling::span")
        ncm = ncm_element.text.strip() if ncm_element else None
        
        # Extrair nome do produto
        nome_element = driver.find_element(By.CLASS_NAME, 'product-name')
        nome_produto = nome_element.text.strip() if nome_element else None
        
        # Extrair categoria
        categoria_element = driver.find_element(By.CLASS_NAME, 'breadcrumb-item')
        categoria = categoria_element.text.strip() if categoria_element else None
        
        # Extrair marca
        marca_element = driver.find_element(By.CLASS_NAME, 'product-brand')
        marca = marca_element.text.strip() if marca_element else None
        
        # Extrair preço médio
        preco_element = driver.find_element(By.CLASS_NAME, 'average-price')
        preco_medio = preco_element.text.strip() if preco_element else None
        
        # Armazenar em variáveis
        produto_info = {
            'ncm': ncm,
            'nome_produto': nome_produto,
            'categoria': categoria,
            'marca': marca,
            'preco_medio': preco_medio
        }
        
        driver.quit()
        return produto_info
    
    except Exception as e:
        print(f"Erro ao consultar o produto: {e}")
        driver.quit()
        return None

# Exemplo de uso
ean = "7894900011517"
produto_info = consulta_produto_ean(ean)
if produto_info:
    print(f"NCM: {produto_info['ncm']}")
    print(f"Nome do Produto: {produto_info['nome_produto']}")
    print(f"Categoria: {produto_info['categoria']}")
    print(f"Marca: {produto_info['marca']}")
    print(f"Preço Médio: {produto_info['preco_medio']}")
else:
    print("Produto não encontrado.")
