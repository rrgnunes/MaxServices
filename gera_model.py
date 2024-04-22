import fdb
from funcoes import os,json,datetime,print_log,parametros
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#carrega config
if os.path.exists("C:/Users/Public/config.json"):
    with open('C:/Users/Public/config.json', 'r') as config_file:
        config = json.load(config_file)
        
    for cnpj in config['sistema']:
        parametros = config['sistema'][cnpj]
        ativo = parametros['sistema_ativo'] == '1'
        sistema_em_uso = parametros['sistema_em_uso_id']
        caminho_base_dados_maxsuport = parametros['caminho_base_dados_maxsuport']
        porta_firebird_maxsuport = parametros['porta_firebird_maxsuport']
        caminho_gbak_firebird_maxsuport = parametros['caminho_gbak_firebird_maxsuport']
        data_hora = datetime.datetime.now()
        data_hora_formatada = data_hora.strftime(
            '%Y_%m_%d_%H_%M_%S')
        print_log('Dados iniciais carregados','apimaxsuport')
        if ativo == 1 and sistema_em_uso == '1':
            # Configuração da Conexão com o Banco de Dados Firebird
            DATABASE_URL = f"firebird+fdb://{parametros.USERFB}:{parametros.PASSFB}@localhost:{porta_firebird_maxsuport}/{caminho_base_dados_maxsuport}"
            fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')

            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)

            # Reflexão do banco de dados
            metadata = MetaData()
            metadata.reflect(engine)
            Base = declarative_base(metadata=metadata)

            # Criar diretório para os modelos, se não existir
            model_dir = "model"
            os.makedirs(model_dir, exist_ok=True)

            for table_name in metadata.tables.keys():
                table = metadata.tables[table_name]
                
                # Gerar código da classe
                class_code = f"""from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class {table_name.capitalize()}(Base):
    __tablename__ = '{table_name}'
"""
                for column in table.columns:
                    # Simplificação para a detecção do tipo; pode precisar de ajustes
                    column_type = str(column.type).split('(')[0]
                    # Verificar se a coluna é chave primária
                    pk = ", primary_key=True" if column.primary_key else ""
                    class_code += f"    {column.name} = Column({column_type}{pk})\n"
                    class_code = class_code.replace('PRECISION','')
                
                # Escrever o código da classe em um arquivo
                with open(os.path.join(model_dir, f"{table_name}.py"), "w") as model_file:
                    model_file.write(class_code)