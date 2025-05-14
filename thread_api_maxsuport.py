from flask import Flask, jsonify, request
import fdb
import mysql.connector
import base64
import parametros
import os
import socket
from funcoes import verifica_dll_firebird, caminho_bd, print_log, crypt, get_local_ip, gera_qr_code, obter_imagem_qrcode
from functools import wraps
from flasgger import Swagger, swag_from
import sys
from flask import make_response

app = Flask(__name__)

# Initialize Flasgger for Swagger documentation
app.config['SWAGGER'] = {
    'title': 'API de Dados',
    'uiversion': 3,
    'description': 'API para gerenciamento de dados com suporte a Firebird e MySQL',
    'version': '1.0'
}
swagger = Swagger(app)

# Database connection configuration
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
        tables = [row[0].strip().lower() for row in cur.fetchall()]
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

@app.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Login'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario': {'type': 'string', 'description': 'Nome de usuário'},
                    'senha': {'type': 'string', 'description': 'Senha do usuário'},
                    'cnpj_empresa': {'type': 'string', 'description': 'CNPJ da empresa'}
                },
                'required': ['usuario', 'senha']
            }
        }
    ],
    'responses': {
        200: {'description': 'Login bem-sucedido', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        400: {'description': 'Usuário e senha são obrigatórios'},
        401: {'description': 'Usuário ou senha inválidos'},
        500: {'description': 'Erro no login'}
    }
})
def login():
    data = request.json
    usuario = data.get('usuario')
    senha = data.get('senha')
    cnpj = data.get('cnpj_empresa', '19775656000104')
    
    if not usuario or not senha:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn
    print_log(f'Tentativa de login usuario {usuario}', 'apidados')
    cur = conn.cursor()
    try:
        if db_type == 'mysql':
            cur.execute("SELECT SENHA FROM USUARIOS WHERE LOGIN = %s AND CNPJ_EMPRESA = %s", (usuario, cnpj,))
        else:
            cur.execute("SELECT SENHA FROM USUARIOS WHERE LOGIN = ? AND CNPJ_EMPRESA = ?", (usuario, cnpj,))
        user = cur.fetchone()
        if user and user[0] == crypt('C', senha):
            return jsonify({'message': 'Login bem-sucedido'})
        else:
            return jsonify({'error': 'Usuário ou senha inválidos'}), 401
    except Exception as e:
        print_log(f'Erro no login:{e}', 'apidados')
        return jsonify({'error': f'Erro no login: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/<db_type>/tables', methods=['GET'])
@require_api_key
@swag_from({
    'tags': ['Tables'],
    'parameters': [
        {'name': 'db_type', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Tipo de banco de dados (mysql ou firebird)'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Lista de tabelas', 'schema': {'type': 'array', 'items': {'type': 'string'}}},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def list_tables(db_type):
    return jsonify(get_table_names())

@app.route('/<table_name>', methods=['GET'])
@require_api_key
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'cnpj_empresa', 'in': 'query', 'type': 'string', 'required': True, 'description': 'CNPJ da empresa'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Dados da tabela', 'schema': {'type': 'array', 'items': {'type': 'object'}}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Tabela não encontrada'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def get_all(table_name):
    cnpj = request.args.get('cnpj_empresa')
    
    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    if db_type == 'firebird':
        cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
        result = cur.fetchone()
        if not result:
            conn.close()
            return jsonify({'error': 'Empresa não encontrada'}), 404
        codigo_empresa = result[0]

        cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
        all_columns = [desc[0].strip().upper() for desc in cur.description]
        empresa_field = next((col for col in all_columns if 'EMPRESA' in col), None)

        if not empresa_field:
            conn.close()
            return jsonify({'error': 'Campo com EMPRESA não encontrado'}), 500

        sql = f"SELECT * FROM {table_name} WHERE {empresa_field} = ?"
        cur.execute(sql, (codigo_empresa,))
    else:
        sql = f"SELECT * FROM {table_name} WHERE CNPJ_EMPRESA = %s"
        cur.execute(sql, (cnpj,))

    columns = [desc[0].strip().lower() for desc in cur.description]
    rows = [convert_blob_to_base64(row, columns) for row in cur.fetchall()]
    conn.close()

    return jsonify(rows)

@app.route('/<table_name>/<int:id>', methods=['GET'])
@require_api_key
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'ID do registro'},
        {'name': 'cnpj_empresa', 'in': 'query', 'type': 'string', 'required': True, 'description': 'CNPJ da empresa'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Registro encontrado', 'schema': {'type': 'object'}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Tabela ou registro não encontrado'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def get_by_id(table_name, id):
    cnpj = request.args.get('cnpj_empresa')
    
    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    empresa_field = 'CNPJ_EMPRESA'


    if db_type == 'firebird':
        cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
        result = cur.fetchone()
        if not result:
            conn.close()
            return jsonify({'error': 'Empresa não encontrada'}), 404
        codigo_empresa = result[0]

        cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
        all_columns = [desc[0].strip().upper() for desc in cur.description]
        empresa_field = next((col for col in all_columns if 'EMPRESA' in col), None)

        if table_name == 'EMPRESA':
            empresa_field = 'CODIGO'

        if not empresa_field:
            conn.close()
            return jsonify({'error': 'Campo com EMPRESA não encontrado'}), 500

        sql = f"SELECT * FROM {table_name} WHERE CODIGO = ? AND {empresa_field} = ?"
        cur.execute(sql, (id, codigo_empresa))
    else:
        sql = f"SELECT * FROM {table_name} WHERE CODIGO = %s AND CNPJ_EMPRESA = %s"
        cur.execute(sql, (id, cnpj))

    columns = [desc[0].strip().lower() for desc in cur.description]

    row = cur.fetchone()

    if row:
        result = convert_blob_to_base64(row, columns)
        conn.close()
        return jsonify(result)
    else:
        conn.close()
        return jsonify({'error': 'Registro não encontrado'}), 404

@app.route('/produto/codigo_barra/<codigo>', methods=['GET'])
@require_api_key
@swag_from({
    'tags': ['Produto'],
    'parameters': [
        {'name': 'codigo', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Código de barras do produto'},
        {'name': 'cnpj_empresa', 'in': 'query', 'type': 'string', 'required': True, 'description': 'CNPJ da empresa'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Produto encontrado', 'schema': {'type': 'array', 'items': {'type': 'object'}}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Tabela ou empresa não encontrada'},
        500: {'description': 'Erro na consulta'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def get_by_barcode(codigo):
    cnpj = request.args.get('cnpj_empresa')

    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    table_name = 'produto'

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if db_type == 'firebird':
            cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            result = cur.fetchone()
            if not result:
                conn.close()
                return jsonify({'error': 'Empresa não encontrada'}), 404
            codigo_empresa = result[0]

            cur.execute("SELECT * FROM PRODUTO_ESTOQUE WHERE 1=0")
            cols_estoque = [desc[0].strip().upper() for desc in cur.description]
            emp_field = next((col for col in cols_estoque if 'EMPRESA' in col), None)
            if not emp_field:
                conn.close()
                return jsonify({'error': 'Campo EMPRESA não encontrado em PRODUTO_ESTOQUE'}), 500

            sql = f"""
                SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO, 
                       COALESCE(PE.ESTOQUE_ATUAL, 0) AS ESTOQUE_ATUAL, PR.CODBARRA,
                       (SELECT FIRST 1 PI.IMAGEM 
                        FROM PRODUTO_IMAGEM PI 
                        WHERE PI.PRODUTO = PR.CODIGO) AS FOTO
                FROM PRODUTO PR
                LEFT JOIN PRODUTO_ESTOQUE PE
                  ON PR.CODIGO = PE.PRODUTO AND PE.{emp_field} = ?
                WHERE PR.{emp_field} = ? AND PR.CODBARRA = ?
            """
            cur.execute(sql, (codigo_empresa, codigo_empresa, codigo))
        else:
            sql = """
                SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO, 
                       COALESCE(PE.ESTOQUE_ATUAL, 0) AS ESTOQUE_ATUAL, PR.CODBARRA,
                       (SELECT PI.IMAGEM 
                        FROM PRODUTO_IMAGEM PI 
                        WHERE PI.PRODUTO = PR.CODIGO 
                        LIMIT 1) AS FOTO
                FROM PRODUTO PR
                LEFT JOIN PRODUTO_ESTOQUE PE
                  ON PR.CODIGO = PE.PRODUTO AND PE.CNPJ_EMPRESA = %s
                WHERE PR.CNPJ_EMPRESA = %s AND PR.CODBARRA = %s
            """
            cur.execute(sql, (cnpj, cnpj, codigo))

        columns = [desc[0].strip().lower() for desc in cur.description]
        row = cur.fetchone()

        if row:
            result = convert_blob_to_base64(row, columns)
            return jsonify([result])
        else:
            return jsonify([])

    except Exception as e:
        return jsonify({'error': f'Erro na consulta: {str(e)}'}), 500

    finally:
        conn.close()

def convert_blob_to_base64(row, columns):
    if isinstance(row, list):
        return [convert_blob_to_base64(r, columns) for r in row]
    
    data = {}
    for i, col in enumerate(columns):
        valor = row[i]

        if hasattr(valor, 'read'):
            valor = valor.read()

        if isinstance(valor, (bytes, bytearray)):
            data[col] = base64.b64encode(valor).decode('utf-8')
        else:
            data[col] = valor
    return data

@app.route('/<table_name>', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'cnpj_empresa': {'type': 'string', 'description': 'CNPJ da empresa'},
                    'additional_fields': {'type': 'object', 'description': 'Campos adicionais para inserção'}
                },
                'required': ['cnpj_empresa']
            }
        }
    ],
    'responses': {
        201: {'description': 'Registro inserido com sucesso', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}, 'codigo': {'type': 'integer'}}}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Empresa não encontrada'},
        500: {'description': 'Erro ao inserir registro'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def insert_into_table(table_name):
    data = request.json
    cnpj = data.get('cnpj_empresa')

    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if db_type == 'firebird':
            cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Empresa não encontrada'}), 404
            codigo_empresa = result[0]

            cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
            all_columns = [desc[0].strip().upper() for desc in cur.description]
            empresa_field = next((col for col in all_columns if 'EMPRESA' in col), None)
            if not empresa_field:
                return jsonify({'error': 'Campo com EMPRESA não encontrado'}), 500

            data[empresa_field.lower()] = codigo_empresa

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())

            cur.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING CODIGO', values)
        else:
            data['cnpj_empresa'] = cnpj
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s' for _ in data])
            values = tuple(data.values())

            cur.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
            cur.execute("SELECT LAST_INSERT_ID()")
        
        produto_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'message': 'Registro inserido com sucesso', 'codigo': produto_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Erro ao inserir registro', 'details': str(e)}), 500

    finally:
        conn.close()

@app.route('/dashboard/metricas', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Dashboard'],
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'cnpj_empresa': {'type': 'string', 'description': 'CNPJ da empresa'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Métricas do dashboard',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'metrics': {
                        'type': 'object',
                        'properties': {
                            'vendas_hoje': {'type': 'number'},
                            'lucro_mensal': {'type': 'number'},
                            'total_pedidos': {'type': 'integer'},
                            'ticket_medio': {'type': 'number'},
                            'pagamento_mais_usado': {'type': 'string'},
                            'produto_mais_vendido': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {'description': 'JSON inválido ou ausente'},
        404: {'description': 'Empresa não encontrada'},
        500: {'description': 'Erro ao obter métricas'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def get_dashboard_metrics():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON inválido ou ausente'}), 400

    cnpj = data.get('cnpj_empresa', '19775656000104')
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        metrics = {}

        if db_type == 'firebird':
            cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Empresa não encontrada'}), 404
            codigo_empresa = result[0]

            def get_empresa_field(tabela):
                cur.execute(f"SELECT * FROM {tabela} WHERE 1=0")
                return next((desc[0].strip().upper() for desc in cur.description if 'EMPRESA' in desc[0].strip().upper()), None)

            f_vendas = get_empresa_field("VENDAS_MASTER")
            f_detalhe = get_empresa_field("VENDAS_DETALHE")
            f_fpg = get_empresa_field("VENDAS_FPG")
            f_produto = get_empresa_field("PRODUTO")

            if not all([f_vendas, f_detalhe, f_fpg, f_produto]):
                return jsonify({'error': 'Campos com EMPRESA não encontrados em todas as tabelas'}), 500

            cur.execute(f"SELECT SUM(TOTAL) FROM VENDAS_MASTER WHERE {f_vendas} = ? AND DATA_EMISSAO BETWEEN CURRENT_DATE AND CURRENT_DATE + 1", (codigo_empresa,))
            metrics['vendas_hoje'] = cur.fetchone()[0] or 0

            cur.execute(f"SELECT SUM(TOTAL) FROM VENDAS_MASTER WHERE {f_vendas} = ? AND EXTRACT(YEAR FROM DATA_EMISSAO) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM DATA_EMISSAO) = EXTRACT(MONTH FROM CURRENT_DATE)", (codigo_empresa,))
            metrics['lucro_mensal'] = cur.fetchone()[0] or 0

            cur.execute(f"SELECT COUNT(*) FROM VENDAS_MASTER WHERE {f_vendas} = ? AND DATA_EMISSAO BETWEEN CURRENT_DATE AND CURRENT_DATE + 1", (codigo_empresa,))
            metrics['total_pedidos'] = cur.fetchone()[0] or 0

            cur.execute(f"SELECT SUM(TOTAL) / COUNT(*) FROM VENDAS_MASTER WHERE {f_vendas} = ? AND DATA_EMISSAO BETWEEN CURRENT_DATE AND CURRENT_DATE + 1", (codigo_empresa,))
            metrics['ticket_medio'] = cur.fetchone()[0] or 0

            cur.execute(f"""
                SELECT FP.DESCRICAO, COUNT(*) 
                FROM VENDAS_FPG VF
                LEFT JOIN FORMA_PAGAMENTO FP ON VF.ID_FORMA = FP.CODIGO
                WHERE VF.VENDAS_MASTER IN (
                    SELECT CODIGO FROM VENDAS_MASTER 
                    WHERE {f_vendas} = ? AND DATA_EMISSAO BETWEEN CURRENT_DATE AND CURRENT_DATE + 1
                )
                GROUP BY FP.DESCRICAO
                ORDER BY COUNT(*) DESC ROWS 1
            """, (codigo_empresa,))
            result = cur.fetchone()
            metrics['pagamento_mais_usado'] = result[0] if result else "Desconhecido"

            cur.execute(f"""
                SELECT P.DESCRICAO, SUM(VI.QTD) 
                FROM VENDAS_DETALHE VI
                JOIN PRODUTO P ON VI.ID_PRODUTO = P.CODIGO
                WHERE VI.{f_detalhe} = ? AND VI.FKVENDA IN (
                    SELECT CODIGO FROM VENDAS_MASTER
                    WHERE {f_vendas} = ? AND DATA_EMISSAO BETWEEN CURRENT_DATE AND CURRENT_DATE + 1
                )
                GROUP BY P.DESCRICAO
                ORDER BY SUM(VI.QTD) DESC ROWS 1
            """, (codigo_empresa, codigo_empresa))
            result = cur.fetchone()
            metrics['produto_mais_vendido'] = result[0] if result else "Nenhum produto"

        else:
            cur.execute("""
                SELECT SUM(TOTAL) FROM VENDAS_MASTER
                WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
            """, (cnpj,))
            metrics['vendas_hoje'] = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT SUM(TOTAL) FROM VENDAS_MASTER
                WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN DATE_FORMAT(NOW(), '%%Y-%%m-01') AND LAST_DAY(NOW())
            """, (cnpj,))
            metrics['lucro_mensal'] = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT COUNT(*) FROM VENDAS_MASTER
                WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
            """, (cnpj,))
            metrics['total_pedidos'] = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT SUM(TOTAL) / COUNT(*) FROM VENDAS_MASTER
                WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
            """, (cnpj,))
            metrics['ticket_medio'] = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT FP.DESCRICAO, COUNT(*) 
                FROM VENDAS_FPG VF
                LEFT JOIN FORMA_PAGAMENTO FP ON VF.ID_FORMA = FP.CODIGO
                WHERE VF.VENDAS_MASTER IN (
                    SELECT CODIGO FROM VENDAS_MASTER 
                    WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
                )
                GROUP BY FP.DESCRICAO
                ORDER BY COUNT(*) DESC
                LIMIT 1
            """, (cnpj,))
            result = cur.fetchone()
            metrics['pagamento_mais_usado'] = result[0] if result else "Desconhecido"

            cur.execute("""
                SELECT P.DESCRICAO, SUM(VI.QTD) 
                FROM VENDAS_DETALHE VI
                JOIN PRODUTO P ON VI.ID_PRODUTO = P.CODIGO
                WHERE VI.CNPJ_EMPRESA = %s AND VI.FKVENDA IN (
                    SELECT CODIGO FROM VENDAS_MASTER 
                    WHERE CNPJ_EMPRESA = %s AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
                )
                GROUP BY P.DESCRICAO
                ORDER BY SUM(VI.QTD) DESC
                LIMIT 1
            """, (cnpj, cnpj))
            result = cur.fetchone()
            metrics['produto_mais_vendido'] = result[0] if result else "Nenhum produto"

        return jsonify({'success': True, 'metrics': metrics})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Erro ao obter métricas', 'details': str(e)}), 500

    finally:
        conn.close()

@app.route('/<table_name>/<int:id>', methods=['PUT'])
@require_api_key
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'ID do registro'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'cnpj_empresa': {'type': 'string', 'description': 'CNPJ da empresa'},
                    'additional_fields': {'type': 'object', 'description': 'Campos para atualização'}
                },
                'required': ['cnpj_empresa']
            }
        }
    ],
    'responses': {
        200: {'description': 'Registro atualizado com sucesso', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        400: {'description': 'CNPJ é obrigatório ou nenhum dado enviado'},
        404: {'description': 'Tabela ou empresa não encontrada'},
        500: {'description': 'Erro ao atualizar'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def update_table(table_name, id):
    data = request.json
    cnpj = data.get('cnpj_empresa')

    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    if not data:
        return jsonify({'error': 'Nenhum dado enviado'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if db_type == 'firebird':
            cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            result = cur.fetchone()
            if not result:
                conn.close()
                return jsonify({'error': 'Empresa não encontrada'}), 404
            codigo_empresa = result[0]

            cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
            all_columns = [desc[0].strip().upper() for desc in cur.description]
            emp_field = next((col for col in all_columns if 'EMPRESA' in col), None)

            if not emp_field:
                conn.close()
                return jsonify({'error': 'Campo EMPRESA não encontrado'}), 500

            update_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            sql = f'UPDATE {table_name} SET {update_clause} WHERE CODIGO = ? AND {emp_field} = ?'
            values = tuple(data.values()) + (id, codigo_empresa)
            cur.execute(sql, values)
        else:
            update_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            sql = f'UPDATE {table_name} SET {update_clause} WHERE CODIGO = %s AND CNPJ_EMPRESA = %s'
            values = tuple(data.values()) + (id, cnpj)
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
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'ID do registro'},
        {'name': 'cnpj_empresa', 'in': 'query', 'type': 'string', 'required': True, 'description': 'CNPJ da empresa'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Registro deletado com sucesso', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Tabela ou empresa não encontrada'},
        500: {'description': 'Erro ao deletar'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def delete_from_table(table_name, id):
    cnpj = request.args.get('cnpj_empresa')
    
    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if db_type == 'firebird':
            cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            result = cur.fetchone()
            if not result:
                conn.close()
                return jsonify({'error': 'Empresa não encontrada'}), 404
            codigo_empresa = result[0]

            cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
            all_columns = [desc[0].strip().upper() for desc in cur.description]
            emp_field = next((col for col in all_columns if 'EMPRESA' in col), None)

            if not emp_field:
                conn.close()
                return jsonify({'error': 'Campo com EMPRESA não encontrado'}), 500

            sql = f'DELETE FROM {table_name} WHERE CODIGO = ? AND {emp_field} = ?'
            cur.execute(sql, (id, codigo_empresa))
        else:
            sql = f'DELETE FROM {table_name} WHERE CODIGO = %s AND CNPJ_EMPRESA = %s'
            cur.execute(sql, (id, cnpj))

        conn.commit()
        return jsonify({'message': 'Registro deletado com sucesso'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Erro ao deletar: {str(e)}'}), 500

    finally:
        conn.close()

@app.route('/qrcode/<int:id>', methods=['GET'])
@require_api_key
@swag_from({
    'tags': ['Data'],
    'parameters': [
        {'name': 'table_name', 'in': 'path', 'type': 'string', 'required': True, 'description': 'Nome da tabela'},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'ID do registro'},
        {'name': 'cnpj_empresa', 'in': 'query', 'type': 'string', 'required': True, 'description': 'CNPJ da empresa'},
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True, 'description': 'Chave de API'}
    ],
    'responses': {
        200: {'description': 'Registro deletado com sucesso', 'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        400: {'description': 'CNPJ é obrigatório'},
        404: {'description': 'Tabela ou empresa não encontrada'},
        500: {'description': 'Erro ao deletar'},
        403: {'description': 'Chave de API inválida ou ausente'}
    }
})
def gerar_qrcode(id):
    # Supondo que o cnpj e a data de vencimento são enviados via request
    cnpj = request.args.get('cnpj_empresa')
    
    if not cnpj:
        return jsonify({'error': 'CNPJ é obrigatório'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    table_name = 'VENDAS_MASTER'

    cur.execute("SELECT CODIGO FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
    result = cur.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Empresa não encontrada'}), 404
    codigo_empresa = result[0]

    cur.execute(f"SELECT * FROM {table_name} WHERE 1=0")
    all_columns = [desc[0].strip().upper() for desc in cur.description]
    emp_field = next((col for col in all_columns if 'EMPRESA' in col), None)

    if not emp_field:
        conn.close()
        return jsonify({'error': 'Campo com EMPRESA não encontrado'}), 500

    sql = f'SELECT CODIGO, TOTAL FROM {table_name} WHERE CODIGO = ? AND {emp_field} = ?'
    cur.execute(sql, (id, codigo_empresa))    
    result = cur.fetchone()

    txid = gera_qr_code(f'Venda numero {id}', result[1])
    
    if txid:
        qr_data = obter_imagem_qrcode(txid)

        if qr_data:
            response = make_response(qr_data)
            response.headers.set('Content-Type', 'image/png')
            return response, 200
        else:
            return jsonify({'error': 'Erro ao obter a imagem QRCode'}), 500
        
    else:    
        return jsonify({'error': 'Erro ao gerar a cobrança'}), 500

if __name__ == '__main__':
    # Geração de chave fixa de 128 bits (16 bytes)
    API_KEY = 'ozYFbdg1WMemus2QRVOEoJugOJzKU8bmxmsCMvH/GB09sTto79au3h+kwltqXNY1PRG2WP/OXPtlz1AMhhWSV/gGaio3b4k9hnaZHu67asT08mE+ybXuMPS1zIp2f0mP'

    # Verifica se um argumento foi passado para definir o banco de dados MySQL
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'dados'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    db_name = 'dados'
    port = 5001
    db_type = 'firebird'
    
    if db_type == 'firebird':
        porta_firebird_maxsuport = 3050
        caminho_base_dados_maxsuport = caminho_bd()[0]
        ip = caminho_bd()[1]        
        client_dll = verifica_dll_firebird()
        fdb.load_api(client_dll)

        host = get_local_ip()

        if host == '192.168.10.115':
            ip = '192.168.10.242'

        FIREBIRD_CONFIG = {
            'dsn': f'{ip}:{caminho_base_dados_maxsuport}',
            'user': parametros.USERFB,
            'password': parametros.PASSFB,
        }

    MYSQL_CONFIG = {
        'host': '10.105.96.106',
        'user': parametros.USERMYSQL,
        'password': parametros.PASSMYSQL,
        'database': db_name
    }

    print_log(f"Conectando ao banco: {db_name}, Porta: {port}, Tipo Banco: {db_type}", 'apidados')
    
    app.run(host='0.0.0.0', port=port, debug=True)