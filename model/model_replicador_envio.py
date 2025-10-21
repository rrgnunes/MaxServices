from model.model_replicador import Replicador

class ReplicadorEnvio(Replicador):

    def __init__(self, conexao_local, conexao_remota):
        super().__init__(conexao_local, conexao_remota)
        self.tipo_replicador = 'envio'


    def buscar_alteracoes_local(self):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()
            cursor.execute("SELECT * FROM REPLICADOR")
            alteracoes = cursor.fetchall()

            if not alteracoes:
                return []

            colunas = [coluna[0] for coluna in cursor.description]
            self._alteracoes = [dict(zip(colunas, linha)) for linha in alteracoes]

        except Exception as e:
            self.logar(f"Erro ao verificar alteracoes -> motivo: {e}\n")

        finally:
            if cursor:
                cursor.close()

    def buscar_relacionamentos(self, tabela: str):
        cursor = None

        try:
            cursor = self.conexao_remota.cursor(dictionary=True)
            
            select = f"""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = '{tabela}'
            """
            
            cursor.execute(select)
            registros = cursor.fetchall()
            
            relacionamentos = []
            for registro in registros:
                tabela_origem = registro['TABLE_NAME']
                coluna_origem = registro['COLUMN_NAME']
                relacionamentos.append((tabela_origem, coluna_origem))
            
            return relacionamentos
        
        except Exception as e:
            self.logar(f"Erro ao buscar relacionamentos da tabela {tabela} -> motivo: {e}\n")
            return None
        
        finally:
            if cursor:
                cursor.close()

    def delete_relacionamento_remoto(self, tabela: str, codigo: int, chave_estrageira: str):
        cursor = None

        try:
            cursor = self.conexao_remota.cursor()

            sql_delete = f"DELETE FROM {tabela} WHERE {chave_estrageira} = {codigo}"
            cursor.execute(sql_delete)

        except Exception as e:
            self.logar(f"Erro ao deletar registro da tabela {tabela} -> motivo: {e}\n")

        finally:
            if cursor:
                cursor.close()

    def retornar_codigo_global(self, tabela: str, codigo_retornado: any, valor: any):
        cursor = None

        try:
            campo_chave_primaria = self.buscar_nome_chave_primaria(tabela)
            cursor = self.conexao_local.cursor()
            sql_update_retorno = f'UPDATE {tabela} SET CODIGO_GLOBAL = {codigo_retornado} WHERE {campo_chave_primaria} = {valor}'
            cursor.execute(sql_update_retorno)
            self.logar(f'Retornou codigo global: {codigo_retornado}\n')

        except Exception as e:
            self.logar(f'Nao foi possivel retornar codigo global -> motivo: {e}\n')

        finally:
            if cursor:
                cursor.close()

    def insert_registro_em_remoto(self, tabela: str, acao: str, dados: dict, valor_chave_primaria: any):
        cursor = None

        try:
            cursor = self.conexao_remota.cursor()
            dados.pop('CODIGO_GLOBAL')
            valores = self.tratar_valores(dados)
            cnpj = self.verifica_empresa_local(tabela, dados)

            if cnpj:
                colunas = ', '.join(dados.keys())
                colunas += ', CNPJ_EMPRESA'
                placeholders = ', '.join(["%s"] * (len(dados) + 1))
                valores.append(cnpj)

            else:
                colunas = ', '.join(dados.keys())
                placeholders = ', '.join(["%s"] * len(dados))

            sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"

            self.logar(f'Insert na tabela {tabela} -> CNPJ: {cnpj}\n')
            cursor.execute(sql_insert, valores)
            codigo_global = cursor._last_insert_id

            self.retornar_codigo_global(tabela, codigo_global, valor_chave_primaria)
            self.marcar_realizado(tabela, acao, valor_chave_primaria, codigo_global)

        except Exception as e:
            self.logar(f"Erro ao inserir dados no MySQL -> motivo: {e}\n")

            if "foreign key constraint fails" in str(e).lower():
                self.logar("Sera adicionado elemento de chave estrangeira...")
                tabela_referenciada, valor_chave_estrangeira = self.extrair_detalhes_chave_estrangeira(e, dados)

                if tabela_referenciada and valor_chave_estrangeira:
                    elemento_firebird = self.buscar_registro_local(tabela_referenciada, valor_chave_estrangeira)
                    self.insert_registro_em_remoto(tabela_referenciada, elemento_firebird)
                    self.insert_registro_em_remoto(tabela, dados, valor_chave_primaria)

        finally:
            if cursor:
                cursor.close()

    def update_registro_em_remoto(self, tabela: str, acao: str, valor_chave_primaria: any, dados: dict):
        cursor = None

        try:
            cursor = self.conexao_remota.cursor()
            codigo_global = dados['CODIGO_GLOBAL']
            if 'CODIGO_GLOBAL' in dados:
                dados.pop('CODIGO_GLOBAL')

            set_clause = ', '.join([f"{coluna} = %s" for coluna in dados.keys()])
            valores = self.tratar_valores(dados)
            cnpj = self.verifica_empresa_local(tabela, dados)
            coluna_chave_primaria = self.buscar_nome_chave_primaria(tabela)

            if cnpj:
                set_clause += ', CNPJ_EMPRESA = %s'
                valores.append(cnpj)

                if codigo_global:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO_GLOBAL = {codigo_global}"

                else:
                    sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s AND CNPJ_EMPRESA = %s"
                    valores.append(valor_chave_primaria)
                    valores.append(cnpj)

            else:
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {coluna_chave_primaria} = %s"
                valores.append(valor_chave_primaria)
            
            self.logar(f'Update na tabela {tabela} -> chave: {valor_chave_primaria} -> cnpj:{cnpj}\n')
            cursor.execute(sql_update, valores)

            self.marcar_realizado(tabela, acao, valor_chave_primaria, codigo_global)

        except Exception as e:
            self.logar(f"Erro ao atualizar dados no MySQL -> motivo: {e}\n")

            if "foreign key constraint fails" in str(e).lower():
                tabela_referenciada, valor_chave_estrangeira = self.extrair_detalhes_chave_estrangeira(e, dados)

            else:
                return

            if tabela_referenciada and valor_chave_estrangeira:            
                elemento_firebird = self.buscar_registro_local(tabela_referenciada, valor_chave_estrangeira)
                self.insert_registro_em_remotol(tabela_referenciada, elemento_firebird)
                self.update_registro_em_remoto(tabela, valor_chave_primaria, dados)

        finally:
            if cursor:
                cursor.close()

    def delete_registro_em_remoto(self, tabela: str, acao: str, valor_chave_primaria: any):
        cursor = None

        try:            
            cursor = self.conexao_remota.cursor()

            if self.empresas:
                cnpj = self.empresas[0]['CNPJ']
            chave_primaria = self.buscar_nome_chave_primaria(tabela)

            if not cnpj:
                return

            self.logar(f"Delete na tabela {tabela} -> chave: {valor_chave_primaria}\n")
            sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = %s and CNPJ_EMPRESA= %s"
            cursor.execute(sql_delete, (valor_chave_primaria, cnpj))

            self.marcar_realizado(tabela, acao, valor_chave_primaria)

        except Exception as e:
            self.logar(f"Erro ao deletar registro da tabela {tabela}: {e}\n")

            if "foreign key constraint fails" in str(e).lower():
                informacao_relacionamento = self.buscar_relacionamentos(tabela)
                tabela_relacionamento = informacao_relacionamento[0][0]
                campo_relacionamento = informacao_relacionamento[0][1]
                self.delete_relacionamento_remoto(tabela_relacionamento, valor_chave_primaria, campo_relacionamento)

        finally:
            if cursor:
                cursor.close()

    def replicar_alteracoes(self):
        self.buscar_alteracoes_local()
        self.remover_referencias_repetidas()

        for alteracao in self._alteracoes_processadas:
            tabela = alteracao['TABELA']
            chave = alteracao['CHAVE']
            acao = alteracao['ACAO']

            self.logar(f'Alterecao realizada: tabela -> {tabela}, acao -> {acao}, chave -> {chave}')

            registro_local = self.buscar_registro_local(tabela, chave)
            
            if registro_local is None and (acao != 'D'):
                self.delete_referencia_replicador(tabela, acao, chave)
                continue

            if acao == 'D' and registro_local:
                acao == 'U'

            if registro_local is None:
                cnpj = self.empresas[0]['CNPJ']
                registro_remoto = self.buscar_registro_remoto(tabela, chave, cnpj)
            
            else:
                cnpj = self.verifica_empresa_local(tabela, registro_local)
                registro_remoto = self.buscar_registro_remoto(tabela, chave, cnpj, registro_local['CODIGO_GLOBAL'])

            if registro_remoto:

                if (acao == 'I') or (acao == 'U'):
                    self.update_registro_em_remoto(tabela, acao, chave, registro_local)

                elif acao == 'D':
                    self.delete_registro_em_remoto(tabela, acao, chave)

            elif registro_local:

                if (acao == 'I') or (acao == 'U'):
                    self.insert_registro_em_remoto(tabela, acao, registro_local, chave)

            else:
                self.delete_referencia_replicador(tabela, acao, chave)
            
            self.commit_pagina()
        
        self.remover_referencias_realizadas()
        self.commit_conexao(True)
        
        self.logar('Finalizado envio dos dados...')

        self.conexao_local.close()
        self.conexao_remota.close()