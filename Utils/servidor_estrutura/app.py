import os
import gravar_estrutura
from flask import Flask, send_from_directory

app = Flask(__name__)


DATA_DIR = os.path.join(os.path.abspath(os.path.join(__file__, '..')), 'data', 'metadados_local')

@app.route('/retorno/<nome_arquivo>', methods=['GET'])
def servir_json(nome_arquivo):
    try:
        if not nome_arquivo.endswith('.json'):
            nome_arquivo += '.json'
        return send_from_directory(DATA_DIR, nome_arquivo)
    except FileNotFoundError:
        return {"erro": "Arquivo não encontrado"}, 404

if __name__ == '__main__':

    try:
        gravar_estrutura.gravar()
    except Exception as e:
        print(f'Não foi possível salvar estrutura do banco de dados -> motivo: {e}')

    app.run(host='192.168.10.236', port=8005)