import importlib

def instalar_biblioteca(biblioteca):
    try:
        importlib.import_module(biblioteca)
        print(f"A biblioteca {biblioteca} já está instalada.")
    except ImportError:
        print(f"A biblioteca {biblioteca} não está instalada. Instalando...")
        try:
            from pip._internal import main as pip_main
        except ImportError:
            from pip import main as pip_main

        pip_main(['install', biblioteca])
        print(f"A biblioteca {biblioteca} foi instalada com sucesso.")

# Exemplo de uso
biblioteca_desejada = "dropbox"
instalar_biblioteca(biblioteca_desejada)
instalar_biblioteca('Pillow')