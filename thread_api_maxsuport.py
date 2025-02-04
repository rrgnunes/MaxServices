from flask import Flask, jsonify, request
import fdb
import mysql.connector
import base64
import parametros
import os
import socket
from funcoes import verifica_dll_firebird, caminho_bd
from functools import wraps

app = Flask(__name__)

def get_db_connection():
    if db_type == 'mysql':
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:
        return fdb.connect(**FIREBIRD_CONFIG)

# Função para listar tabelas do banco
def get_table_names():
    conn = get_db_connection()
    cur = conn.cursor()
    if db_type == 'mysql':
        cur.execute("SHOW TABLES")
        tables = [row[0] for row in cur.fetchall()]
    else:
        cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND rdb$system_flag = 0")
        tables = [row[0].strip().lower() for row in cur.fetchall()]
    conn.close()
    return tables

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

# Função para converter blobs em base64
def convert_blob_to_base64(row, columns):
    data = {}
    for i, col in enumerate(columns):
        if isinstance(row[i], (bytes, bytearray)):
            data[col] = base64.b64encode(row[i]).decode('utf-8')
        else:
            data[col] = row[i]
    return data

@app.route('/<db_type>/tables', methods=['GET'])
@require_api_key
def list_tables(db_type):
    return jsonify(get_table_names(db_type))

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
        if db_type == 'mysql':
            cur.execute(f"""SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO , PE.ESTOQUE_ATUAL ,
                            (SELECT PI.IMAGEM 
                                FROM PRODUTO_IMAGEM PI 
                                WHERE PI.PRODUTO = PR.CODIGO 
                                LIMIT 1) AS FOTO
                        FROM PRODUTO PR
                        left outer join PRODUTO_ESTOQUE PE
                          on PR.CODIGO = PE.PRODUTO
                        WHERE PR.CODBARRA = %s""", (codigo,))
        else:
            cur.execute(f""""SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO , PE.ESTOQUE_ATUAL ,
                            (SELECT FIRST 1 PI.IMAGEM 
                                FROM PRODUTO_IMAGEM PI 
                                WHERE PI.PRODUTO = PR.CODIGO 
                                ) AS FOTO
                        FROM PRODUTO PR
                        left outer join PRODUTO_ESTOQUE PE
                          on PR.CODIGO = PE.PRODUTO
                        WHERE CODBARRA = ?""", (codigo,))
        columns = [desc[0].strip().lower() for desc in cur.description]
        row = cur.fetchone()

        if row:
            result = convert_blob_to_base64(row, columns)
            return jsonify([result])  # Retorna sempre como uma lista
        else:
            return jsonify([])  # Retorna lista vazia se não encontrar

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
    if not data:
        return jsonify({'error': 'Nenhum dado enviado'}), 400  # Verifica se há dados para atualizar

    conn = get_db_connection()
    cur = conn.cursor()

    # Define os placeholders corretos para cada tipo de banco de dados
    if db_type == 'mysql':
        update_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        sql = f'UPDATE {table_name} SET {update_clause} WHERE codigo = %s'
    else:  # SQLite
        update_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        sql = f'UPDATE {table_name} SET {update_clause} WHERE codigo = ?'

    values = tuple(data.values()) + (id,)

    try:
        cur.execute(sql, values)
        conn.commit()
        return jsonify({'message': 'Registro atualizado com sucesso'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()


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
    # Geração de chave fixa de 128 bits (16 bytes)
    API_KEY = 'ozYFbdg1WMemus2QRVOEoJugOJzKU8bmxmsCMvH/GB09sTto79au3h+kwltqXNY1PRG2WP/OXPtlz1AMhhWSV/gGaio3b4k9hnaZHu67asT08mE+ybXuMPS1zIp2f0mP'
    db_type = 'firebird'

    # Configurações do banco Firebird
    porta_firebird_maxsuport = 3050
    caminho_base_dados_maxsuport = caminho_bd()[0]
    ip = caminho_bd()[1]

    if db_type == 'firebird':
        client_dll = verifica_dll_firebird()
        fdb.load_api(client_dll)

    FIREBIRD_CONFIG = {
        'dsn': f'{ip}:{caminho_base_dados_maxsuport}',
        'user': parametros.USERFB,
        'password': parametros.PASSFB,
    }

    # Configurações do banco MySQL
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': parametros.USERMYSQL,
        'password': parametros.PASSMYSQL,
        'database': 'dados'
    }

    app.run(host='0.0.0.0', port=5000, debug=True)
