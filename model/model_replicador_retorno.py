from model.model_replicador import Replicador

class ReplicadorRetorno(Replicador):

    def __init__(self, conexao_local, conexao_remota):
        super().__init__(conexao_local, conexao_remota)
        self.tipo_replicador = 'receber'

    def buscar_alteracoes_replicador_remoto(self):
        cursor = None
        
        try:
            alteracoes = []

            if self.empresas != None:
                cursor = self.conexao_remota.cursor(dictionary=True)

                for empresa in self.empresas:
                    cursor.execute(f"SELECT * FROM REPLICADOR WHERE CNPJ_EMPRESA = {empresa['CNPJ']}")
                    result = cursor.fetchall()
                    alteracoes += result

            self._alteracoes = alteracoes

        except Exception as e:
            self.logar(f"Erro ao verificar alteracoes -> motivo: {e}\n")
        
        finally:
            if cursor:
                cursor.close()

    def retornar_valor_chave_primaria_gerada(self, tabela: str, campo_chave_primaria: str, valor_chave_primaria: any, codigo_global: any):        
        cursor = None

        try:
            cursor = self.conexao_remota.cursor()
            sql_update = f'UPDATE {tabela} SET {campo_chave_primaria} = {valor_chave_primaria} WHERE CODIGO_GLOBAL = {codigo_global}'
            cursor.execute(sql_update)

            self.logar(f'Valor de chave primaria retornado: {valor_chave_primaria}\n')

        except Exception as e:
            self.logar(f'Erro ao retornar valor de chave primaria -> motivo: {e}\n')

        finally:
            if cursor:
                cursor.close()        

    def insert_registro_em_local(self, tabela: str, acao: str, dados: dict):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()

            if tabela.lower() == 'vendas_detalhe':
                codigo_master = dados['CODIGO_GLOBAL_MASTER']
                cursor.execute(f'select codigo from vendas_master where codigo_global = {codigo_master}')
                codigo = cursor.fetchone()[0]
                dados['FKVENDA'] = codigo

            colunas = ', '.join(dados.keys())
            placeholders = ', '.join(['?'] * len(dados))
            valores = self.tratar_valores(dados)
            campo_chave_primaria = self.buscar_nome_chave_primaria(tabela)

            sql_insert = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders}) RETURNING {campo_chave_primaria}"

            self.logar(f'Insert na tabela {tabela}\n')
            cursor.execute(sql_insert, valores)
            valor_chave_primaria = cursor.fetchone()[0]

            codigo_global = None
            if tabela.lower() != 'relatorios':
                codigo_global = dados['CODIGO_GLOBAL']
                self.retornar_valor_chave_primaria_gerada(tabela, campo_chave_primaria, valor_chave_primaria, codigo_global)

            cnpj = self.verifica_empresa_local(tabela, dados)
            self.marcar_realizado(tabela, acao, valor_chave_primaria, codigo_global, cnpj)

        except Exception as e:
            self.logar(f"Erro ao inserir dados no Firebird: {e}\n")

        finally:
            if cursor:
                cursor.close()

    def update_registro_em_local(self, tabela: str, acao: str, valor_chave_primaria: str, dados: dict,  codigo_global: int = None):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()
            set_clause = ', '.join([f"{coluna} = ?" for coluna in dados.keys()])
            chave_primaria = self.buscar_nome_chave_primaria(tabela)

            if not valor_chave_primaria and not codigo_global:
                return

            if valor_chave_primaria:
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE {chave_primaria} = ?"
                valores = self.tratar_valores(dados)
                valores.append(valor_chave_primaria)

            elif codigo_global:
                valor_chave_primaria = self.verifica_valor_chave_primaria(tabela, codigo_global, chave_primaria)
                dados[chave_primaria] = valor_chave_primaria
                sql_update = f"UPDATE {tabela} SET {set_clause} WHERE CODIGO_GLOBAL = ?"
                valores = self.tratar_valores(dados)
                valores.append(codigo_global)

            self.logar(f'Update na tabela {tabela} -> chave: {valor_chave_primaria} ou codigo global: {codigo_global}\n')
            cursor.execute(sql_update, valores)

            cnpj = self.verifica_empresa_local(tabela, dados)
            self.marcar_realizado(tabela, acao, valor_chave_primaria, codigo_global, cnpj)

        except Exception as e:
            self.logar(f"Erro ao atualizar dados no Firebird -> motivo: {e}\n")

        finally:
            if cursor:
                cursor.close()

    def delete_registro_em_local(self, tabela: str, acao: str, valor_chave_primaria: any, codigo_global: int = None):
        cursor = None

        try:
            cursor = self.conexao_local.cursor()

            if codigo_global:
                sql_delete = f"DELETE FROM {tabela} WHERE CODIGO_GLOBAL = {codigo_global}"

            elif valor_chave_primaria:
                chave_primaria = self.buscar_nome_chave_primaria(tabela)
                sql_delete = f"DELETE FROM {tabela} WHERE {chave_primaria} = {valor_chave_primaria}"

            else:
                return

            self.logar(f'Delete na tabela: {tabela} -> chave: {valor_chave_primaria} ou codigo global: {codigo_global}')
            cursor.execute(sql_delete)
            
            self.marcar_realizado(tabela, acao, valor_chave_primaria, codigo_global)

        except Exception as e:
            self.logar(f"Erro ao deletar registro da tabela {tabela}: {e}\n")

        finally:
            if cursor:
                cursor.close()

    def replicar_alteracoes(self):
        self.buscar_alteracoes_replicador_remoto()
        self.remover_referencias_repetidas()

        for alteracao in self._alteracoes_processadas:
            tabela = alteracao.get('TABELA', '')
            acao = alteracao.get('ACAO', '')
            chave = alteracao.get('CHAVE', '')
            cnpj = alteracao.get('CNPJ_EMPRESA', '')
            codigo_global = alteracao.get('CODIGO_GLOBAL', '')

            self.logar(f'Alteracao realizada: tabela -> {tabela}, acao -> {acao}, chave -> {chave}, codigo_global -> {codigo_global}, cnpj -> {cnpj}')

            registro_remoto = self.buscar_registro_remoto(tabela, chave, cnpj, codigo_global)
            registro_local = self.buscar_registro_local(tabela, chave, codigo_global)

            if registro_local:

                if (acao == 'I') or (acao == 'U'):
                    self.update_registro_em_local(tabela, acao, chave, registro_remoto, codigo_global)

                elif acao == 'D':
                    self.delete_registro_em_local(tabela, acao, chave, codigo_global)

            elif registro_remoto:

                if (acao == 'I') or (acao == 'U'):
                    self.insert_registro_em_local(tabela, acao, registro_remoto)

            else:
                self.delete_referencia_replicador(tabela, acao, chave, codigo_global, cnpj)


            self.commit_pagina()

        self.commit_conexao(True)

        self.remover_referencias_realizadas()
        self.logar('Finalizado recebimento de dados...\n')
        
        self.conexao_remota.close()
        self.conexao_local.close()