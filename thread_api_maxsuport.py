from flask import Flask, jsonify, request
import fdb
import base64
import parametros

app = Flask(__name__)

porta_firebird_maxsuport = 3050
caminho_base_dados_maxsuport = r"c:\maxsuport_rian\dados\dados.fdb"
fdb.load_api('c:\\maxsuport\\fbclient.dll')

# Configurações do banco Firebird
DB_CONFIG = {
    'dsn': f'192.168.10.242:{caminho_base_dados_maxsuport}',
    'user': f'{parametros.USERFB}',
    'password': f'{parametros.PASSFB}',
}

def get_db_connection():
    return fdb.connect(**DB_CONFIG)

def get_table_names():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND rdb$system_flag = 0")
    tables = [row[0].strip().lower() for row in cur.fetchall()]
    conn.close()
    return tables

def convert_blob_to_base64(row, columns):
    data = {}
    for i, col in enumerate(columns):
        if isinstance(row[i], fdb.fbcore.BlobReader):
            data[col] = base64.b64encode(row[i].read()).decode('utf-8')
        else:
            data[col] = row[i]
    return data

@app.route('/<table_name>', methods=['GET'])
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

@app.route('/<table_name>/<int:id>', methods=['GET'])
def get_by_id(table_name, id):
    if table_name not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table_name} WHERE codigo = ?', (id,))
    columns = [desc[0].strip().lower() for desc in cur.description]
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify(convert_blob_to_base64(row, columns))
    else:
        return jsonify({'error': 'Registro não encontrado'}), 404

@app.route('/<table_name>', methods=['POST'])
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
