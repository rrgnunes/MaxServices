import fdb
import pathlib
import configparser
from fdb.fbcore import Cursor

#  Icinia a migração dos dados
def migra_entidade(conn: fdb.Connection):
    entidades = ['VENDEDOR', 'MOTORISTA', 'TRANSPORTADOR']
    cur:Cursor = conn.cursor()
    codigo = ultimo_codigo_pessoa(conn)
    novo_codigo = 0 + codigo
    try:
        chaves = obter_chaves_estrangerias(conn)
        apagar_chaves_estrangeiras(conn, chaves)


        for entidade in entidades:
            dados = registros_origem(conn, entidade)
            
            for registro in dados['registros']:
                novo_codigo += 1
                print(registro['codigo'], novo_codigo)
                insert_registros_pessoa(conn, registro, dados['sql_insert'], novo_codigo)
                atualiza_codigo_pessoa(conn, registro['codigo'], novo_codigo, entidade)
                update_campos(conn, entidade, registro['codigo'], novo_codigo)

        cur.close()
        criar_chaves_estrangeiras(conn, chaves)
    except Exception as e:
        conn.rollback()
        print(e)

# Atualiza os campos relacionados com os novos códigos gerados
def update_campos(conn: fdb.Connection, entidade, codigo, novo_codigo) -> None:
    cur:Cursor = conn.cursor()
    tabelas_campos = tabelas_chaves_relacionadas(cur, entidade)
    try:
        for tabela, campo in tabelas_campos:
            # campos que devem ser ignorados para update
            if 'CODIGO_PESSOA' in campo:
                continue
            elif 'CPF_' in campo:
                continue
            elif ('EMPRESA' in tabela) and ('TRANSPORTADORA' in campo):
                continue
            elif ('TRANSPORTADORA' in tabela) and ('MOTORISTA' in campo):
                continue
            sql = f'update {tabela} set {campo} = {novo_codigo} where {campo} = {codigo}'
            print(sql)
            cur.execute(sql)
        cur.close()
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Não foi possivel atualizar os campos de relacionamento da entidade: {e} - {entidade} - {tabela} <=> {campo}')

# insere os dados das tabelas na tabela de pessoas
def insert_registros_pessoa(conn: fdb.Connection, registro: dict, sql: str, novo_codigo: int) -> None:
    cur:Cursor = conn.cursor()
    elementos = list(registro.values())
    elementos[0] = novo_codigo
    try:
        print(sql, elementos)
        cur.execute(sql, elementos)
        cur.close()
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Erro ao inserir registro: {e} - {registro}')

# atualiza o campo codigo_pessoa na tabela de origem
def atualiza_codigo_pessoa(conn: fdb.Connection, codigo: int, novo_codigo: int, entidade: str):
    cur:Cursor = conn.cursor()
    sqls = []
    try:
        if entidade == 'VENDEDOR':
            sql_pessoa = f'update vendedores set codigo_pessoa = {novo_codigo} where codigo = {codigo}'
            sql_codigo_vendedor = f'update vendedores set codigo = {novo_codigo} where codigo = {codigo}'
            sqls.append(sql_pessoa)
            sqls.append(sql_codigo_vendedor)
        elif entidade == 'MOTORISTA':
            sql_pessoa = f'insert into motorista (codigo_pessoa, CODIGO_PESSOA_TRANSPORTADORA) values ({novo_codigo}, {codigo})'
            sqls.append(sql_pessoa)
        elif entidade == 'TRANSPORTADOR':
            sql_pessoa = f'update transportadora set codigo_pessoa = {novo_codigo} where codigo = {codigo}'
            sql_vinculo_motorista = f'update motorista set codigo_pessoa_transportadora = {novo_codigo} where codigo_pessoa_transportadora = {codigo}'
            sqls.append(sql_pessoa)
            sqls.append(sql_vinculo_motorista)

        for sql in sqls:
            print(sql)
            cur.execute(sql)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f'Não foi possível atualizar codigo_pessoa - motivo: {e} - entidade: {entidade} - codigo: {codigo} - novo codigo: {novo_codigo}')
    finally:
        if cur:
            cur.close()

# verificar qual é o ultimo código de pessoa cadastrado
def ultimo_codigo_pessoa(conn: fdb.Connection) -> int:
    cur:Cursor = conn.cursor()
    try:
        
        cur.execute('select max(codigo) from pessoa')
        codigo = cur.fetchone()[0]
        cur.close()
        return codigo

    except Exception as e:
        print(f'Ocorreu um erro ao tentar verificar ultimo codigo de pessoa: {e}')

# Pega os dados das tabelas a serem migradas
def registros_origem(conn: fdb.Connection, tabela) -> dict:
    cur:Cursor = conn.cursor()
    dados = {}
    try:
        if tabela == 'VENDEDOR':

            colunas = ['codigo', 'tipo', 'razao', 'fantasia', 'codmun', 'uf', 'empresa', 'ie', 'cep', 'municipio', 'forn', 'fun', 'cli', 'fab', 'tran', 'adm', 'ativo', 'isento', 'entidade']

            sql_select = """select
                                codigo, 'FÍSICA' as tipo, nome as razao, nome as fantasia,
                                '0' as codmun, 'MT' as uf, '1' as empresa, '' as ie, '' as cep,
                                '' as municipio, 'N' as forn, 'N' as fun, 'N' as cli, 'N' as fab,
                                'N' as tran, 'N' as adm, 'S' as ativo, '2' as isento, '32' as entidade
                            from vendedores"""
            
        elif tabela == 'TRANSPORTADOR':

            colunas = ['codigo', 'tipo', 'cnpj', 'ie', 'razao', 'fantasia', 'endereco', 'numero', 'bairro', 'codmun', 'municipio', 'uf', 'cep', 'ativo', 'empresa', 'forn', 'fun', 'cli', 'fab', 'tran', 'adm', 'isento', 'entidade']

            sql_select = """select
                                codigo, pessoa as tipo, cnpj, ie, nome as razao, apelido as fantasia, endereco,
                                numero, bairro, cod_cidade as codmun, cidade as municipio, uf, cep, ativo, empresa, 'N' as forn,
                                'N' as fun, 'N' as cli, 'N' as fab, 'S' as tran, 'N' as adm,
                                case when (ie is not null and (trim(ie) <> '') ) then '0' else '2'  end as isento,
                                '16' as entidade
                            from transportadora"""

        elif tabela == 'MOTORISTA':

            colunas = ['codigo', 'tipo', 'razao', 'fantasia', 'cnpj', 'codmun', 'uf', 'empresa', 'ie', 'cep', 'municipio', 'forn', 'fun', 'cli', 'fab', 'tran', 'adm', 'ativo', 'isento', 'entidade']

            sql_select = """select
                                codigo, 'FÍSICA' as tipo, motorista as razao, motorista as fantasia, cpf_motorista as cnpj,
                                '0' as codmun, 'MT' as uf, '1' as empresa, '' as ie, '' as cep,
                                '' as municipio, 'N' as forn, 'N' as fun, 'N' as cli, 'N' as fab,
                                'N' as tran, 'N' as adm, 'S' as ativo, '2' as isento, '64' as entidade
                            from transportadora
                            where motorista <> '' and motorista is not null"""

        cur.execute(sql_select)
        registros = cur.fetchall()

        registros = [dict(zip([col for col in colunas], registro)) for registro in registros]

        # trocar as colunas com valores null para ''
        for registro in registros:
            for chave in registro.keys():
                if registro[chave] == None:
                    registro[chave] = ''

        dados['registros'] = registros
        dados['sql_insert'] = f"insert into pessoa ({','.join([col for col in colunas])}) values ({','.join(['?']*len(colunas))})"

        cur.close()
        return dados
    except Exception as e:
        print(e)

# verifica todos os campos do banco de dados que possui o nome da entidade
def tabelas_chaves_relacionadas(cur:Cursor, entidade) -> list:
    try:
        sql = f"""SELECT
                    r.RDB$RELATION_NAME AS TABELA,
                    f.RDB$FIELD_NAME AS COLUNA
                FROM
                    RDB$RELATION_FIELDS f
                JOIN
                    RDB$RELATIONS r ON r.RDB$RELATION_NAME = f.RDB$RELATION_NAME
                JOIN
                    RDB$FIELDS d ON d.RDB$FIELD_NAME = f.RDB$FIELD_SOURCE
                LEFT JOIN
                    RDB$TYPES t ON t.RDB$FIELD_NAME = 'RDB$FIELD_TYPE' AND t.RDB$TYPE = d.RDB$FIELD_TYPE
                WHERE
                    r.RDB$SYSTEM_FLAG = 0 and f.rdb$field_name like '%{entidade}%'
                ORDER BY
                    r.RDB$RELATION_NAME, f.RDB$FIELD_POSITION"""
        cur.execute(sql)
        tabelas_campos = cur.fetchall()
        tabelas_campos_formatados = [(tabela_campo[0].strip(), tabela_campo[1].strip()) for tabela_campo in tabelas_campos]
        return tabelas_campos_formatados
    except Exception as e:
        print(f'Erro ao pegar as tabelas relacionadas ao campo: {e} - entidade: {entidade}')

# Consulta todas as chaves estrangeiras do banco de dados
def obter_chaves_estrangerias(conn: fdb.Connection) -> list | None:
    sql = """
        SELECT 
            trim(rc.RDB$CONSTRAINT_NAME) AS chave_estrangeira,
            trim(rc.RDB$RELATION_NAME) AS tabela,
            trim(idxseg.RDB$FIELD_NAME) AS coluna,
            trim(refidx.RDB$RELATION_NAME) AS tabela_referenciada,
            trim(refidxseg.RDB$FIELD_NAME) AS coluna_referenciada
        FROM 
            RDB$RELATION_CONSTRAINTS rc
        JOIN 
            RDB$REF_CONSTRAINTS refc ON rc.RDB$CONSTRAINT_NAME = refc.RDB$CONSTRAINT_NAME
        JOIN 
            RDB$RELATION_CONSTRAINTS refrelc ON refc.RDB$CONST_NAME_UQ = refrelc.RDB$CONSTRAINT_NAME
        JOIN 
            RDB$INDEX_SEGMENTS idxseg ON rc.RDB$INDEX_NAME = idxseg.RDB$INDEX_NAME
        JOIN 
            RDB$INDEX_SEGMENTS refidxseg ON refrelc.RDB$INDEX_NAME = refidxseg.RDB$INDEX_NAME
        JOIN 
            RDB$INDICES refidx ON refrelc.RDB$INDEX_NAME = refidx.RDB$INDEX_NAME
        ORDER BY 
            tabela, chave_estrangeira, coluna;"""
    try:
        cur:Cursor = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        return result
    except Exception as e:
        print(f'Erro ao obter chaves: {e}')

# Apaga as chaves estrangeiras consultadas
def apagar_chaves_estrangeiras(conn: fdb.Connection, dados: list):
    apagou = False
    ultima_chave = ''
    cur:Cursor = conn.cursor()
    try:

        for dado in dados:
            if ultima_chave == dado[0]:
                print(f'Chave {dado[0]} ja apagado!')
                continue
            sql = f'alter table {dado[1]} drop constraint {dado[0]};'
            print(sql)
            cur.execute(sql)
            ultima_chave = dado[0]

        conn.commit()
        apagou = True
        return apagou
    except Exception as e:
        print(f'Erro ao tentar apagar chaves estrangeiras: {e}')
        return apagou

# Recria as chaves apagadas, exceto as de remessa e de retorno
def criar_chaves_estrangeiras(conn: fdb.Connection, dados: list):
    cur:Cursor = conn.cursor()
    ultimas_chaves = []
    num_vezes = 0
    try:

        for dado in dados:

            nova_chave = f'FK_{dado[1]}'

            if 'remessa' in nova_chave.lower():
                continue
            elif 'retorno' in nova_chave.lower():
                continue

            if nova_chave in ultimas_chaves:
                num_vezes += 1
                nova_chave_icrementada = f'{nova_chave}_{num_vezes}'
                sql = f'alter table {dado[1]} add constraint {nova_chave_icrementada} foreign key ({dado[2]}) references {dado[3]}({dado[4]});'
            else:
                num_vezes = 0
                sql = f'alter table {dado[1]} add constraint {nova_chave} foreign key ({dado[2]}) references {dado[3]}({dado[4]});'
            print(sql)
            cur.execute(sql)
            ultimas_chaves.append(nova_chave)

        conn.commit()

    except Exception as e:
        print(f'Não foi possivel criar as chaves estrangeiras: {e}')

if __name__ == '__main__':

    ROOT   = pathlib.Path(__file__).parent.parent
    INI_FILE = ROOT / 'Banco.ini'
    
    parser = configparser.ConfigParser()
    parser.read(INI_FILE)

    path  = parser.get('BD', 'path')
    ip    = parser.get('BD', 'ip')
    porta = parser.get('BD', 'porta')
    dsn   = f'{ip}/{porta}:{path}'

    try:
        conn = fdb.connect(dsn=dsn,
                        user='maxsuport',
                        password='oC8qUsDp')
        
        print('Conexão Firebird estabelecida com sucesso...')
        print()
        
        with conn:
            
            migra_entidade(conn)

    except Exception as e:
        print(f'Ocorreu um erro durante a conexão: {e}')