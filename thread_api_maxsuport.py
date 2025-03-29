from flask import Flask, jsonify, request
import fdb
import mysql.connector
import base64
import parametros
import os
import socket
from funcoes import verifica_dll_firebird, caminho_bd, print_log, crypt
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
def login():
    data = request.json
    usuario = data.get('usuario')
    senha = data.get('senha')
    cnpj = data.get('cnpj_empresa')
    cnpj = '19775656000104'
    
    if not usuario or not senha:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn  # Retorna erro se houver problema de conexão
    print_log(f'Tentativa de login usuario {usuario}','apidados')
    cur = conn.cursor()
    try:
        if db_type == 'mysql':
            cur.execute("SELECT SENHA FROM USUARIOS WHERE LOGIN = %s AND CNPJ_EMPRESA = %s", (usuario,cnpj,))
        else:
            cur.execute("SELECT SENHA FROM USUARIOS WHERE LOGIN = ? AND CNPJ_EMPRESA = ?", (usuario,cnpj,))
        user = cur.fetchone()
        if user[0] == crypt('C',senha):
            return jsonify({'message': 'Login bem-sucedido'})
        else:
            return jsonify({'error': 'Usuário ou senha inválidos'}), 401
    except Exception as e:
        print_log(f'Erro no login:{e}','apidados')
        return jsonify({'error': f'Erro no login: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/<db_type>/tables', methods=['GET'])
@require_api_key
def list_tables(db_type):
    return jsonify(get_table_names(db_type))

@app.route('/<table_name>', methods=['GET'])
@require_api_key
def get_all(table_name):
    data = request.json    
    cnpj = data.get('cnpj_empresa')   
     
    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    
    if db_type == 'mysql':        
        cur.execute(f"SELECT * FROM {table_name} WHERE CNPJ_EMPRESA = %s", (cnpj,))    
    else:
        cur.execute(f"SELECT * FROM {table_name} WHERE CNPJ_EMPRESA = ?", (cnpj,))    
    
    columns = [desc[0].strip().lower() for desc in cur.description]
    rows = [convert_blob_to_base64(row, columns) for row in cur.fetchall()]
    conn.close()
    
    return jsonify(rows)

@app.route('/produto/codigo_barra/<codigo>', methods=['GET'])
@require_api_key
def get_by_barcode(codigo):
    data = request.json    
    cnpj = data.get('cnpj_empresa')   
    
    table_name = 'produto'  # Substitua pelo nome correto da tabela

    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        sql = ''
        if db_type == 'mysql':
            sql = """SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO, 
                            COALESCE(PE.ESTOQUE_ATUAL, 0) AS ESTOQUE_ATUAL, PR.CODBARRA,
                            (SELECT PI.IMAGEM 
                            FROM PRODUTO_IMAGEM PI 
                            WHERE PI.PRODUTO = PR.CODIGO 
                            LIMIT 1) AS FOTO
                    FROM PRODUTO PR
                    LEFT JOIN PRODUTO_ESTOQUE PE
                    ON PR.CODIGO = PE.PRODUTO AND PE.CNPJ_EMPRESA = %s
                    WHERE PR.CNPJ_EMPRESA = %s AND PR.CODBARRA = %s"""
        else:
            sql = """SELECT PR.CODIGO, PR.DESCRICAO, PR.PR_VENDA, PR.PR_CUSTO, 
                            COALESCE(PE.ESTOQUE_ATUAL, 0) AS ESTOQUE_ATUAL, PR.CODBARRA,
                            (SELECT FIRST 1 PI.IMAGEM 
                            FROM PRODUTO_IMAGEM PI 
                            WHERE PI.PRODUTO = PR.CODIGO) AS FOTO
                    FROM PRODUTO PR
                    LEFT JOIN PRODUTO_ESTOQUE PE
                    ON PR.CODIGO = PE.PRODUTO AND PE.CNPJ_EMPRESA = ?
                    WHERE PR.CNPJ_EMPRESA = ? AND PR.CODBARRA = ?"""
            
        cur.execute(sql, (cnpj,cnpj,codigo,))
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

def convert_blob_to_base64(row, columns):
    if isinstance(row, list):
        return [convert_blob_to_base64(r, columns) for r in row]
    
    data = {}
    for i, col in enumerate(columns):
        if isinstance(row[i], (bytes, bytearray)):
            data[col] = base64.b64encode(row[i]).decode('utf-8')
        else:
            data[col] = row[i]
    return data

@app.route('/<table_name>/consulta', methods=['POST'])
@require_api_key
def consulta_banco(table_name):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON inválido ou ausente'}), 400

    cnpj = data.get('cnpj_empresa')
    codigo = data.get('codigo_produto')
    
    if codigo == 'null':
        codigo = ''
    
    if not cnpj:
        cnpj = '19775656000104'
        #return jsonify({'error': 'CNPJ é obrigatório'}), 400
    
    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if db_type == 'mysql':
        if codigo:
            cur.execute(f"SELECT * FROM {table_name.upper()} WHERE CODIGO = %s AND CNPJ_EMPRESA = %s", (codigo, cnpj))
        else:
            cur.execute(f"SELECT * FROM {table_name.upper()} WHERE CNPJ_EMPRESA = %s LIMIT 10", (cnpj,))
    else:  # Firebird
        if codigo:
            cur.execute(f"SELECT * FROM {table_name} WHERE CODIGO = ? AND CNPJ_EMPRESA = ?", (codigo, cnpj))
        else:
            cur.execute(f"SELECT FISRT 10 * FROM {table_name} WHERE CNPJ_EMPRESA = ?", (cnpj,))
    
    columns = [desc[0].strip().lower() for desc in cur.description]
    rows = cur.fetchall()
    conn.close()
    
    if rows:
        return jsonify({"produtos": convert_blob_to_base64(rows, columns)})
    else:
        return jsonify({'error': 'Registro não encontrado'}), 404

@app.route('/<table_name>', methods=['POST'])
@require_api_key
def insert_into_table(table_name):
    data = request.json
    cnpj = data.get('cnpj_empresa')       
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Inserindo o produto na tabela PRODUTO
        columns = ', '.join(data.keys()) + ', cnpj_empresa'  # Adiciona o campo manualmente
        placeholders = ', '.join(['?' for _ in data]) + ', ?'  # Adiciona um placeholder extra
        values = tuple(data.values()) + (cnpj,)  # Adiciona o valor do CNPJ


        cur.execute(f'INSERT INTO PRODUTO ({columns}) VALUES ({placeholders}) RETURNING CODIGO', values)
        produto_id = cur.fetchone()[0]  # Obtém o código do produto inserido
        conn.commit()

        # Inserindo na tabela PRODUTO_ESTOQUE
        estoque_data = (
            produto_id,
            data.get('empresa', 1),  # Empresa fornecida ou padrão 1
            data.get('qtd_atual', 0),
            data.get('cnpj_empresa','')
        )

        cur.execute(
            'INSERT INTO PRODUTO_ESTOQUE (PRODUTO, EMPRESA, ESTOQUE_ATUAL, CNPJ_EMPRESA) VALUES (?, ?, ?, ?)',
            estoque_data
        )
        conn.commit()

        return jsonify({'message': 'Produto e estoque inseridos com sucesso', 'codigo': produto_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Erro ao inserir registro', 'details': str(e)}), 500
    finally:
        conn.close()

@app.route('/dashboard/metricas', methods=['POST'])
@require_api_key
def get_dashboard_metrics():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON inválido ou ausente'}), 400

    cnpj = data.get('cnpj_empresa', '19775656000104')
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        metrics = {}
        
        # Vendas Hoje
        cur.execute(f"SELECT SUM(TOTAL) AS vendas_hoje FROM VENDAS_MASTER WHERE CNPJ_EMPRESA = '{cnpj}' AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY")
        metrics['vendas_hoje'] = cur.fetchone()[0] or 0
        
        # Lucro Mensal
        cur.execute("SELECT SUM(TOTAL) AS lucro_mensal FROM VENDAS_MASTER WHERE CNPJ_EMPRESA = '{cnpj}' AND  DATA_EMISSAO BETWEEN DATE_FORMAT(NOW(), '%Y-%m-01') AND LAST_DAY(NOW())")
        metrics['lucro_mensal'] = cur.fetchone()[0] or 0
        
        # Total de Pedidos do Dia
        cur.execute("SELECT COUNT(*) AS total_pedidos FROM VENDAS_MASTER WHERE CNPJ_EMPRESA = '{cnpj}' AND  DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY")
        metrics['total_pedidos'] = cur.fetchone()[0] or 0
        
        # Ticket Médio
        cur.execute("SELECT SUM(TOTAL) / COUNT(*) AS ticket_medio FROM VENDAS_MASTER WHERE CNPJ_EMPRESA = '{cnpj}' AND  DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY")
        metrics['ticket_medio'] = cur.fetchone()[0] or 0
        
        # Forma de Pagamento Mais Usada
        cur.execute("SELECT FP.DESCRICAO , COUNT(*) AS qtd FROM VENDAS_FPG VF LEFT OUTER JOIN FORMA_PAGAMENTO FP ON VF.ID_FORMA  = FP.CODIGO WHERE VF.VENDAS_MASTER IN (SELECT CODIGO FROM VENDAS_MASTER VM WHERE VM.CNPJ_EMPRESA = 'cnpj}' AND DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY) GROUP BY FP.DESCRICAO ORDER BY qtd DESC LIMIT 1")
        result = cur.fetchone()
        metrics['pagamento_mais_usado'] = result[0] if result else "Desconhecido"
        
        # Produto Mais Vendido do Dia
        cur.execute("SELECT P.DESCRICAO, SUM(VI.QTD) AS qtd_vendida FROM VENDAS_DETALHE VI JOIN PRODUTO P ON VI.ID_PRODUTO = P.CODIGO WHERE VI.CNPJ_EMPRESA = '{cnpj}' AND  VI.FKVENDA IN (SELECT CODIGO FROM VENDAS_MASTER VM WHERE VM.CNPJ_EMPRESA = '{cnpj}' AND  DATA_EMISSAO BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY) GROUP BY P.DESCRICAO ORDER BY qtd_vendida DESC LIMIT 1")
        result = cur.fetchone()
        metrics['produto_mais_vendido'] = result[0] if result else "Nenhum produto"
        
        conn.close()
        
        return jsonify({'success': True, 'metrics': metrics})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Erro ao obter métricas', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/<table_name>/<int:id>', methods=['PUT'])
@require_api_key
def update_table(table_name, id):
    data = request.json
    cnpj = data.get('cnpj_empresa')      
        
    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    data = request.json
    if not data:
        return jsonify({'error': 'Nenhum dado enviado'}), 400  # Verifica se há dados para atualizar

    conn = get_db_connection()
    cur = conn.cursor()

    # Define os placeholders corretos para cada tipo de banco de dados
    if db_type == 'mysql':
        update_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        sql = f'UPDATE {table_name} SET {update_clause} WHERE codigo = %s  AND EMPRESA  = %s'
    else:  # Firebird
        update_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        sql = f'UPDATE {table_name} SET {update_clause} WHERE codigo = ? AND EMPRESA  = ?'

    values = tuple(data.values()) + (id,cnpj,)

    try:
        cur.execute(sql, values)
        conn.commit()

        # Atualizado na tabela PRODUTO_ESTOQUE
        estoque_data = (
            data.get('qtd_atual', 0),
            id,
            cnpj,
        )

        cur.execute(
            'UPDATE PRODUTO_ESTOQUE SET ESTOQUE_ATUAL = ? WHERE PRODUTO = ? AND CNPJ_EMPRESA = ?',
            estoque_data
        )
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
    data = request.json
    cnpj = data.get('cnpj_empresa')        
    
    if table_name.lower() not in get_table_names():
        return jsonify({'error': 'Tabela não encontrada'}), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM {table_name} WHERE codigo = ? and cnpj_empresa = ?', (id,cnpj,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Registro deletado com sucesso'})

import sys


if __name__ == '__main__':
    # Geração de chave fixa de 128 bits (16 bytes)
    API_KEY = 'ozYFbdg1WMemus2QRVOEoJugOJzKU8bmxmsCMvH/GB09sTto79au3h+kwltqXNY1PRG2WP/OXPtlz1AMhhWSV/gGaio3b4k9hnaZHu67asT08mE+ybXuMPS1zIp2f0mP'

    # Verifica se um argumento foi passado para definir o banco de dados MySQL
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'dados'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000  # Porta passada como argumento ou 5000 por padrão

    db_name = 'dados'
    port = 5001  # Porta passada como argumento ou 5000 por padrão
    db_type = 'mysql'
    
    if db_type == 'firebird':
        # Configurações do banco Firebird
        porta_firebird_maxsuport = 3050
        caminho_base_dados_maxsuport = caminho_bd()[0]
        ip = caminho_bd()[1]        
        client_dll = verifica_dll_firebird()
        fdb.load_api(client_dll)

        FIREBIRD_CONFIG = {
            'dsn': f'{ip}:{caminho_base_dados_maxsuport}',
            'user': parametros.USERFB,
            'password': parametros.PASSFB,
        }

    # Configurações do banco MySQL
    MYSQL_CONFIG = {
        'host': '10.105.96.106',
        'user': parametros.USERMYSQL,
        'password': parametros.PASSMYSQL,
        'database': db_name  # Nome do banco vindo por parâmetro
    }

    print_log(f"Conectando ao banco: {db_name}, Porta: {port}",'apidados')
    
    app.run(host='0.0.0.0', port=port, debug=True)

