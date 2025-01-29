from flask import Flask, jsonify, request
import fdb
import base64
import parametros
import os
from functools import wraps

app = Flask(__name__)

# Geração de chave fixa de 128 bits (16 bytes)
API_KEY = 'ozYFbdg1WMemus2QRVOEoJugOJzKU8bmxmsCMvH/GB09sTto79au3h+kwltqXNY1PRG2WP/OXPtlz1AMhhWSV/gGaio3b4k9hnaZHu67asT08mE+ybXuMPS1zIp2f0mP'
# print(f"Sua chave de API é: {API_KEY}")  # Salve essa chave em algum lugar seguro

# Configurações do banco Firebird
porta_firebird_maxsuport = 3050
caminho_base_dados_maxsuport = r"c:\\maxsuport_rian\\dados\\dados.fdb"
fdb.load_api('c:\\maxsuport\\fbclient64.dll')

DB_CONFIG = {
    'dsn': f'192.168.10.242:{caminho_base_dados_maxsuport}',
    'user': parametros.USERFB,
    'password': parametros.PASSFB,
}

# Função para criar conexão com o banco
def get_db_connection():
    return fdb.connect(**DB_CONFIG)

# Função para listar tabelas do banco
def get_table_names():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND rdb$system_flag = 0")
    tables = [row[0].strip().lower() for row in cur.fetchall()]
    conn.close()
    return tables

# Função para converter blobs em base64
def convert_blob_to_base64(row, columns):
    data = {}
    for i, col in enumerate(columns):
        if isinstance(row[i], fdb.fbcore.BlobReader):
            blob_data = row[i].read()
            data[col] = base64.b64encode(blob_data).decode('utf-8')
        else:
            data[col] = row[i]
    return data

# Middleware para validar a chave da API
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('Authorization')
        if key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Chave de API inválida ou ausente'}), 403
    return decorated_function

# Endpoints

@app.route('/<table_name>', methods=['GET'])
@require_api_key
def get_all(table_name):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table_name}')
    columns = [desc[0].strip().lower() for desc in cur.description]
    rows = [convert_blob_to_base64(row, columns) for row in cur.fetchall()]
    conn.close()
    
    return jsonify(rows)

@app.route('/produto/codigo_barra/<codigo>', methods=['GET'])
@require_api_key
def get_by_barcode(codigo):
    table_name = 'produto'  # Substitua pelo nome correto da tabela

    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT * FROM {table_name} WHERE CODBARRA = ?", (codigo,))
        columns = [desc[0].strip().lower() for desc in cur.description]
        row = cur.fetchone()

        if row:
            result = convert_blob_to_base64(row, columns)
            return jsonify(result)
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404

    except Exception as e:
        return jsonify({'error': f'Erro na consulta: {str(e)}'}), 500

    finally:
        conn.close()

@app.route('/<table_name>/<int:id>', methods=['GET'])
@require_api_key
def get_by_id(table_name, id):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table_name} WHERE codigo = ?', (id,))
    columns = [desc[0].strip().lower() for desc in cur.description]
    row = cur.fetchone()

    if row:
        result = convert_blob_to_base64(row, columns)
        conn.close()
        return jsonify(result)
    else:
        conn.close()
        return jsonify({'error': 'Registro não encontrado'}), 404

@app.route('/<table_name>', methods=['POST'])
@require_api_key
def insert_into_table(table_name):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    values = tuple(data.values())

    cur.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Registro inserido com sucesso'}), 201

@app.route('/<table_name>/<int:id>', methods=['PUT'])
@require_api_key
def update_table(table_name, id):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    update_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = tuple(data.values()) + (id,)

    cur.execute(f'UPDATE {table_name} SET {update_clause} WHERE codigo = ?', values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Registro atualizado com sucesso'})

@app.route('/<table_name>/<int:id>', methods=['DELETE'])
@require_api_key
def delete_from_table(table_name, id):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM {table_name} WHERE codigo = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Registro deletado com sucesso'})

if __name__ == '__main__':
    app.run(host='192.168.10.115', port=5000, debug=True)
