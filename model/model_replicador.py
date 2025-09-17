import os
import re
import sys
import datetime
from mysql import connector
from fdb import Connection, DatabaseError, fbcore

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from funcoes.funcoes import print_log

class Replicador:

    def __init__(self, conexao_local: Connection, conexao_remota: connector.MySQLConnection):
        self.conexao_local = conexao_local
        self.conexao_remota = conexao_remota
        self._nome_servico = ''
        self.tipo_replicador = None
        self.empresas = []
        self._chaves_primarias = {}
        self._alteracoes = []
        self._alteracoes_processadas = []
        self._alteracoes_realizadas = []
        self.testar_conexao_local()
        self.testar_conexao_remota()
        self.consulta_empresas_local()

    @property
    def nome_servico(self):
        return self._nome_servico
    
    @nome_servico.setter
    def nome_servico(self, nome):
        if not nome:
            self.logar('O nome do servico nao pode ser vazio')
            raise ValueError('O nome do servico nao pode ser vazio')
        
        if isinstance(nome, str):
            self._nome_servico = nome
        else:
            self.logar(f'O nome do servico deve ser uma string ao inves de {type(nome)}')
            raise TypeError(f'O nome do servico deve ser uma string ao inves de {type(nome)}')

    def testar_conexao_local(self):
        cursor = None
        try:
            cursor = self.conexao_local.cursor()
            cursor.execute('SELECT 1 FROM RDB$DATABASE;')
            cursor.close()
            print('Conexao firebird esta ativa...')
        except:
            self.logar('Erro na conexão da base de dados local')
            raise DatabaseError('Erro na conexão da base de dados local')
        finally:
            if cursor:
                cursor.close()

    def testar_conexao_remota(self):
        try:
            self.conexao_remota.ping()
            print('Conexao MySql esta ativa...')
        except:
            self.logar('Erro na conexão da base de dados remota')
            raise connector.DatabaseError('Erro na conexão da base de dados remota')
        
    def logar(self, msg):
        print_log(msg, self.nome_servico)

    def tratar_valores(self, dados: dict):
        valores = []
        for key, valor in dados.items():

            if isinstance(valor, fbcore.BlobReader):
                blob = valor.read()
                valores.append(blob)
                valor.close()

            elif isinstance(valor, datetime.timedelta):
                total_de_segundos = valor.total_seconds()
                horas = int(total_de_segundos // 3600)
                segundos_restantes = total_de_segundos % 3600
                minutos = int(segundos_restantes // 60)
                segundos_restantes = segundos_restantes % 60
                valor = datetime.time(hour=horas, minute=minutos, second=int(segundos_restantes))
                valores.append(valor)

            else:
                valores.append(valor)

        return valores
    
    def verifica_empresa_local(self, tabela:str, dados: dict):
        codigo_empresa = 0

        if tabela == 'EMPRESA':
            codigo_empresa = dados['CODIGO']

        else:

            for coluna, valor in dados.items():

                if 'EMPRESA' in coluna.upper():

                    if isinstance(valor, int):
                        codigo_empresa = valor
                        break

                elif 'EMITENTE' in coluna.upper():

                    if isinstance(valor, int):
                        codigo_empresa = valor
                        break
        cnpj = ''

        if codigo_empresa > 0:

            for empresa in self.empresas:

                if empresa['CODIGO'] == codigo_empresa:
                    cnpj = empresa['CNPJ']
                    return cnpj

            cursor = None

            try:
                cursor = self.conexao_local.cursor()
                cursor.execute(f'SELECT CNPJ FROM EMPRESA WHERE CODIGO = {codigo_empresa}')
                cnpj = cursor.fetchall()[0][0]

            except Exception as e:
                self.logar(f'Nao foi possivel consultar empresa: {e}')
            
            finally:
                if cursor:
                    cursor.close()
        else:
            cnpj = self.empresas[0]['CNPJ']

        return cnpj
    
    def buscar_nome_chave_primaria(self, tabela: str):
        cursor = None
        campo_chave_primaria = self._chaves_primarias.get(tabela, '')

        if campo_chave_primaria:
            return campo_chave_primaria

        try:
            cursor = self.conexao_local.cursor()

            select_codigo = f"""
            SELECT TRIM(RDB$FIELD_NAME)
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = '{tabela}' AND UPPER(RDB$FIELD_NAME) = 'CODIGO'
            """
            cursor.execute(select_codigo)
            campo_chave_primaria = cursor.fetchone()
            
            if campo_chave_primaria:
                self._chaves_primarias[tabela] = campo_chave_primaria[0]
                return 'CODIGO' 
            
            select = f"""
            SELECT TRIM(segments.RDB$FIELD_NAME)
            FROM RDB$RELATION_CONSTRAINTS constraints
            JOIN RDB$INDEX_SEGMENTS segments ON constraints.RDB$INDEX_NAME = segments.RDB$INDEX_NAME
            WHERE constraints.RDB$RELATION_NAME = '{tabela}'
            AND constraints.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
            """
            cursor.execute(select)
            campo_chave_primaria = cursor.fetchone()
            
            if campo_chave_primaria:
                self._chaves_primarias[tabela] = campo_chave_primaria[0]
                return campo_chave_primaria[0]
            
            return None
            
        except Exception as e:
            self.logar(f"Erro ao buscar nome da chave primária no Firebird: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()
        
    def buscar_registro_local(self, tabela: str, chave: str, codigo_global = None):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()

            if codigo_global:
                sql_select = f'SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = {codigo_global}'
                cursor.execute(sql_select)
                dados = cursor.fetchone()

                if not dados:
                    chave_primaria = self.buscar_nome_chave_primaria(tabela)

                    if not chave_primaria:
                        self.logar(f"Chave primária não encontrada para a tabela {tabela}")
                        return None
                    
                    if not chave:
                        return None

                    sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{chave}'"
                    cursor.execute(sql_select)
                    dados = cursor.fetchone()

            else:
                chave_primaria = self.buscar_nome_chave_primaria(tabela)

                if not chave_primaria:
                    self.logar(f"Chave primária não encontrada para a tabela {tabela}.")
                    return None
                
                sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = '{chave}'"

                cursor.execute(sql_select)

                dados = cursor.fetchone()

            if dados:
                colunas = [desc[0] for desc in cursor.description]
                dados = dict(zip(colunas, dados))

            else:
                self.logar(f'Não há elemento Firebird com esta chave - chave: {chave} (pode ter sido excluido ou precisa ser adicionado!)\n')

            return dados

        except Exception as e:
            self.logar(f"Erro ao buscar elemento no Firebird: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()

    def buscar_registro_remoto(self, tabela: str, codigo: int, cnpj: str ='', codigo_global = None):
        cursor = None
        
        try:
            cursor = self.conexao_remota.cursor(dictionary=True)

            if codigo_global:
                sql_select = f"SELECT * FROM {tabela} WHERE CODIGO_GLOBAL = %s"
                cursor.execute(sql_select, (codigo_global,))

            else:
                chave_primaria = self.buscar_nome_chave_primaria(tabela)

                if not chave_primaria:
                    self.logar(f"Chave primária não encontrada para a tabela {tabela}.")
                    return None
                
                if tabela.lower() == 'relatorios':
                    sql_select = f'SELECT * FROM {tabela} WHERE {chave_primaria} = %s'
                    cursor.execute(sql_select, (codigo,))

                else:
                    sql_select = f"SELECT * FROM {tabela} WHERE {chave_primaria} = %s AND CNPJ_EMPRESA = %s"
                    cursor.execute(sql_select, (codigo, cnpj))

            dados = cursor.fetchone()

            if not dados:
                self.logar(f'Não há elemento que possua esta chave no Mysql - chave: {codigo} ou este código global: {codigo_global}')
                return None
            
            dados = dict(dados)
            dados.pop('CNPJ_EMPRESA')

            return dados
        except Exception as e:
            self.logar(f"Erro ao buscar elemento MySQL: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()

    def verifica_valor_chave_primaria(self, tabela:str, codigo_global:str, chave_primaria:str):
        elemento = self.buscar_registro_local(tabela, None, codigo_global)
        return elemento.get(chave_primaria, None)
    
    def consulta_empresas_local(self):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()
            cursor.execute('SELECT CODIGO, CNPJ FROM EMPRESA')
            empresas = cursor.fetchall()

            if not empresas:
                return None
            
            self.empresas = [{'CODIGO': codigo, 'CNPJ': cnpj} for codigo, cnpj in empresas]

        except Exception as e:
            self.logar(f'Erro ao consultar os cnpjs locais -> motivo: {e}')
        
        finally:
            if cursor:
                cursor.close()

    def extrair_detalhes_chave_estrangeira(self, erro, dados):
        match = re.search(r"FOREIGN KEY \(`(.+?)`\) REFERENCES `(.+?)` \(`(.+?)`\)", str(erro))
        if match:
            coluna_chave_estrangeira = match.group(1)
            tabela_referenciada = match.group(2)
            valor_chave_estrangeira = dados.get(coluna_chave_estrangeira)
            return tabela_referenciada, valor_chave_estrangeira
        return None, None

    def remover_referencias_repetidas(self):
        
        for referencia in self._alteracoes:

            if referencia not in self._alteracoes_processadas:
                self._alteracoes_processadas.append(referencia)

            else:
                self.delete_referencia_replicador(
                    referencia.get('TABELA', ''),
                    referencia.get('ACAO', ''),
                    referencia.get('CHAVE', ''),
                    referencia.get('CODIGO_GLOBAL', '')
                )

    def marcar_realizado(self, tabela: str, acao: str, valor_chave_primaria: any, codigo_global: int = None, cnpj: str = None):
        self._alteracoes_realizadas.append({
            "TABELA": tabela,
            "ACAO" : acao,
            "CHAVE": valor_chave_primaria,
            "CODIGO_GLOBAL": codigo_global,
            "CNPJ": cnpj,
        })

    def remover_referencias_realizadas(self):
    
        for referencia in self._alteracoes_realizadas:
            self.delete_referencia_replicador(
                referencia.get('TABELA', ''),
                referencia.get('ACAO', ''),
                referencia.get('CHAVE', ''),
                referencia.get('CODIGO_GLOBAL', ''),
                referencia.get('CNPJ', '')
            )

    def delete_referencia_replicador(self, tabela:str, acao:str, chave:str, codigo_global:str = 0, cnpj:str=''):
        cursor = None

        if self.tipo_replicador == 'envio':

            try:
                sql_delete = "DELETE FROM REPLICADOR WHERE chave = ? AND tabela = ? AND acao = ? ROWS 1;"
                cursor = self.conexao_local.cursor()
                cursor.execute(sql_delete, (chave, tabela, acao,))

                self.conexao_local.commit()

            except fbcore.DatabaseError as e:
                self.logar(f"Erro ao deletar registros da tabela REPLICADOR: {e}\n")
                self.conexao_local.rollback()

            finally:
                if cursor:
                    cursor.close()
                    
        elif self.tipo_replicador == 'receber':

            try:                

                if codigo_global:
                    sql_delete = "DELETE FROM REPLICADOR WHERE TABELA = %s AND ACAO = %s AND CODIGO_GLOBAL = %s LIMIT 1;"
                    valores = tabela, acao, codigo_global

                else:
                    sql_delete = "DELETE FROM REPLICADOR WHERE CHAVE = %s AND TABELA = %s AND ACAO = %s AND CNPJ_EMPRESA = %s LIMIT 1;"
                    valores = chave, tabela, acao, cnpj

                cursor = self.conexao_remota.cursor()
                cursor.execute(sql_delete, valores)

                self.conexao_remota.commit()

            except Exception as e:
                self.logar(f"Erro ao deletar registros da tabela REPLICADOR: {e}\n")
                self.conexao_remota.rollback()

            finally:
                if cursor:
                    cursor.close()