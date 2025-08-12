import os
import shutil
import py_compile

pasta_local = os.path.abspath(os.path.dirname(__file__))
pasta_raiz = pasta_local.replace('MaxServices_compilado', '')

pasta_funcoes = os.path.join(pasta_raiz, 'funcoes')
pasta_threads = os.path.join(pasta_raiz, 'threads')
pasta_credenciais = os.path.join(pasta_raiz, 'credenciais')



def compilar():

    py_compile.compile(os.path.join(pasta_raiz, 'scheduler.py'))
    shutil.move(os.path.join(pasta_raiz, '__pycache__', 'scheduler.cpython-311.pyc'), os.path.join(pasta_local, 'scheduler.pyc'))

    verificar_e_compilar_arquivos(pasta_credenciais)
    copiar_arquivos_compilados(pasta_credenciais)
    
    verificar_e_compilar_arquivos(pasta_funcoes)
    copiar_arquivos_compilados(pasta_funcoes)

    verificar_e_compilar_arquivos(pasta_threads)
    copiar_arquivos_compilados(pasta_threads)


def criar_pasta_destino(destino):
    caminho_pasta_destino = os.path.join(pasta_local, destino)
    if not os.path.exists(caminho_pasta_destino):
        os.makedirs(caminho_pasta_destino)
    return caminho_pasta_destino

def verificar_e_compilar_arquivos(pasta):
    for file in os.listdir(pasta):
        if os.path.isfile(os.path.join(pasta, file)) and (file != '__init__.py') and (str(file).endswith('.py')):
            caminho_arquivo = os.path.join(pasta, file)
            print(f'Compilando o arquivo: {file}')
            py_compile.compile(caminho_arquivo)

def copiar_arquivos_compilados(pasta_origem):
    print('Copiando arquivos compilados para pasta de destino.')
    pasta_cache = os.path.join(pasta_origem, '__pycache__')
    arquivos_compilados = os.listdir(pasta_cache)
    pasta_destino = criar_pasta_destino(os.path.basename(pasta_origem))

    for arquivo in arquivos_compilados:
        if not '__init__' in arquivo:
            shutil.move(os.path.join(pasta_cache, arquivo), os.path.join(pasta_destino, arquivo.replace('.cpython-311', '')))


if __name__ == '__main__':

    compilar()