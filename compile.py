import os
import shutil
import py_compile

pasta_raiz = os.path.abspath(os.path.dirname(__file__))

pasta_funcoes = os.path.join(pasta_raiz, 'funcoes')
pasta_threads = os.path.join(pasta_raiz, 'threads')
pasta_credenciais = os.path.join(pasta_raiz, 'credenciais')
pasta_model = os.path.join(pasta_raiz, 'model')

pasta_final = os.path.join(pasta_raiz, 'SERVER')


def compilar():
    criar_pasta_destino(pasta_final)
    criar_pasta_destino(os.path.join(pasta_final, 'utils'))

    verificar_e_compilar_arquivos(os.path.join(pasta_raiz, 'scheduler.py'))
    shutil.move(os.path.join(pasta_raiz, '__pycache__', 'scheduler.cpython-311.pyc'), os.path.join(pasta_final, 'scheduler.pyc'))

    verificar_e_compilar_arquivos(os.path.join(pasta_raiz, 'utils', 'salva_metadados_json.py'))
    shutil.move(os.path.join(pasta_raiz, 'utils', '__pycache__', 'salva_metadados_json.cpython-311.pyc'), os.path.join(pasta_final, 'utils', 'salva_metadados_json.pyc'))

    verificar_e_compilar_arquivos(pasta_credenciais)
    copiar_arquivos_compilados(pasta_credenciais)
    
    verificar_e_compilar_arquivos(pasta_funcoes)
    copiar_arquivos_compilados(pasta_funcoes)

    verificar_e_compilar_arquivos(pasta_threads)
    copiar_arquivos_compilados(pasta_threads)

    verificar_e_compilar_arquivos(pasta_model)
    copiar_arquivos_compilados(pasta_model)    

    copiar_dependencias()


def criar_pasta_destino(destino):
    caminho_pasta_destino = os.path.join(pasta_final, destino)
    if not os.path.exists(caminho_pasta_destino):
        os.makedirs(caminho_pasta_destino)
    return caminho_pasta_destino

def verificar_e_compilar_arquivos(item):
    if os.path.isdir(item):
        for file in os.listdir(item):
            if os.path.isfile(os.path.join(item, file)) and (file != '__init__.py') and (str(file).endswith('.py')):
                caminho_arquivo = os.path.join(item, file)
                print(f'Compilando o arquivo: {file}')
                py_compile.compile(caminho_arquivo)
    elif os.path.isfile(item):
        print(f'Compilando o arquivo: {item}')
        py_compile.compile(item)

def copiar_arquivos_compilados(pasta_origem):
    print('Copiando arquivos compilados para pasta de destino.')
    pasta_cache = os.path.join(pasta_origem, '__pycache__')
    arquivos_compilados = os.listdir(pasta_cache)
    pasta_destino = criar_pasta_destino(os.path.basename(pasta_origem))

    for arquivo in arquivos_compilados:
        if not '__init__' in arquivo:
            shutil.move(os.path.join(pasta_cache, arquivo), os.path.join(pasta_destino, arquivo.replace('.cpython-311', '')))

def copiar_dependencias():
    print('Copiando dependencias...')
    pastas_dep = [
        'libs',
        'Ico'
    ]
    for pasta in pastas_dep:
        shutil.copytree(os.path.join(pasta_raiz, pasta), os.path.join(pasta_final, pasta))


if __name__ == '__main__':

    compilar()