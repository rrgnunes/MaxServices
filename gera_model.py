import fdb
from funcoes import os, json, datetime, print_log, parametros
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

print("Iniciando o processo...")

# Carrega config
if os.path.exists("config.json"):
    print("Arquivo de configuração encontrado.")
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        
    for cnpj in config['sistema']:
        dados_cnpj = config['sistema'][cnpj]
        ativo = dados_cnpj['sistema_ativo'] == '1'
        sistema_em_uso = dados_cnpj['sistema_em_uso_id']
        caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
        porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
        caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
        data_hora = datetime.datetime.now()
        data_hora_formatada = data_hora.strftime('%Y_%m_%d_%H_%M_%S')
        
        print_log('Dados iniciais carregados', 'apimaxsuport')
        print(f"Processando CNPJ: {cnpj}")

        if ativo and sistema_em_uso == '1':
            print("Sistema ativo, iniciando conexão com o banco de dados...")
            
            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}\\fbclient.dll')
            print("Biblioteca fbclient.dll carregada com sucesso.")

            # Configuração da Conexão com o Banco de Dados Firebird
            DATABASE_URL = f"firebird+fdb://{parametros.USERFB}:{parametros.PASSFB}@192.168.10.242:{porta_firebird_maxsuport}/{caminho_base_dados_maxsuport}?charset=latin1"
            print("URL do banco de dados configurada.")

            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)
            print("Engine SQLAlchemy criada com sucesso.")

            # Reflexão do banco de dados
            metadata = MetaData()
            print("Refletindo metadados do banco...")
            metadata.reflect(engine)
            Base = declarative_base(metadata=metadata)
            print(f"Reflexão concluída. Tabelas encontradas: {list(metadata.tables.keys())}")

            # Criar diretório para os modelos, se não existir
            model_dir = "model"
            os.makedirs(model_dir, exist_ok=True)
            print(f"Diretório {model_dir} criado/verificado.")

            for table_name in metadata.tables.keys():
                table = metadata.tables[table_name]
                print(f"Gerando modelo para a tabela: {table_name}")

                # Gerar código da classe
                class_code = f"""from sqlalchemy import Column, INTEGER, DOUBLE, CHAR, TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from thread_api_maxsuport import db  # Importando a instância corretamente

class {table_name.capitalize()}(db.Model):
    __tablename__ = '{table_name}'
"""
                for column in table.columns:
                    # Simplificação para a detecção do tipo; pode precisar de ajustes
                    column_type = str(column.type).split('(')[0]
                    # Verificar se a coluna é chave primária
                    pk = ", primary_key=True" if column.primary_key else ""
                    class_code += f"    {column.name} = Column({column_type}{pk})\n"
                    class_code = class_code.replace('PRECISION', '')

                # Escrever o código da classe em um arquivo
                model_file_path = os.path.join(model_dir, f"{table_name}.py")
                with open(model_file_path, "w", encoding="utf-8") as model_file:
                    model_file.write('# -*- coding: utf-8 -*-\n')  # Adiciona declaração de codificação
                    model_file.write(class_code)
                print(f"Arquivo de modelo criado: {model_file_path}")


            print("Processo concluído com sucesso.")
        else:
            print(f"Sistema inativo ou não configurado para este CNPJ: {cnpj}")

print("Execução finalizada.")
