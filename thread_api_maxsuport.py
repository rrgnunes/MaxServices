import fdb
from funcoes import threading,os,json,datetime,print_log,parametros
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session,sessionmaker,declarative_base
from model.mesa import Base, Mesa
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Body
from sqlalchemy.ext.declarative import declarative_base
from typing import Type, Generic, TypeVar, List, Dict, Any
import os
import importlib.util

Base = declarative_base()

def import_all_models(directory_path: str):
    for filename in os.listdir(directory_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]  # Remove '.py' do final para obter o nome do módulo
            module_path = os.path.join(directory_path, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

# Caminho para o diretório 'model'. Ajuste conforme necessário.
models_directory_path = os.path.join(os.path.dirname(__file__), 'model')
import_all_models(models_directory_path)


# thread do backup
class threadapimaxsuport(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    def run(self):
        self.apimaxsuport()
        
    def apimaxsuport(self):

        #carrega config
        if os.path.exists("C:/Users/Public/config.json"):
            with open('C:/Users/Public/config.json', 'r') as config_file:
                config = json.load(config_file)
                
            for cnpj in config['sistema']:
                dados_cnpj = config['sistema'][cnpj]
                ativo = dados_cnpj['sistema_ativo'] == '1'
                sistema_em_uso = dados_cnpj['sistema_em_uso_id']
                caminho_base_dados_maxsuport = dados_cnpj['caminho_base_dados_maxsuport']
                porta_firebird_maxsuport = dados_cnpj['porta_firebird_maxsuport']
                caminho_gbak_firebird_maxsuport = dados_cnpj['caminho_gbak_firebird_maxsuport']
                data_hora = datetime.datetime.now()
                data_hora_formatada = data_hora.strftime(
                    '%Y_%m_%d_%H_%M_%S')
                print_log('Dados iniciais carregados','apimaxsuport')
                if ativo == 1 and sistema_em_uso == '1':
                    # Configuração da Conexão com o Banco de Dados Firebird
                    DATABASE_URL = f"firebird+fdb://{parametros.USERFB}:{parametros.PASSFB}@localhost:{porta_firebird_maxsuport}/{caminho_base_dados_maxsuport}?charset=None"
                    fdb.load_api(f'{caminho_gbak_firebird_maxsuport}/fbclient.dll')
                    engine = create_engine(DATABASE_URL)
                    
                    # Vincular a base declarativa ao engine
                    Base.metadata.create_all(engine)
                    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

                    app = FastAPI()

                    # Dependência para obter a sessão do SQLAlchemy
                    def get_db():
                        db = SessionLocal()
                        try:
                            yield db
                        finally:
                            db.close()

                    T = TypeVar('T', bound=Base)

                    # Definição da classe CRUDBase atualizada
                    class CRUDBase(Generic[T]):
                        # Definições anteriores...

                        def create(self, db: Session, obj_in: Dict[str, Any]) -> T:
                            db_obj = self.model(**obj_in)
                            db.add(db_obj)
                            db.commit()
                            db.refresh(db_obj)
                            return db_obj

                        def update(self, db: Session, id: int, obj_in: Dict[str, Any]) -> T:
                            db_obj = db.query(self.model).get(id)
                            if db_obj:
                                for field, value in obj_in.items():
                                    setattr(db_obj, field, value)
                                db.commit()
                                db.refresh(db_obj)
                            return db_obj

                        def delete(self, db: Session, id: int) -> None:
                            obj = db.query(self.model).get(id)
                            db.delete(obj)
                            db.commit()

                    def create_model_schema(model: Type[Base]) -> Type[BaseModel]:
                        fields = {column.name: (column.type.python_type, ...) for column in model.__table__.columns}
                        model_schema = type(f"{model.__name__}Schema", (BaseModel,), fields)
                        return model_schema

                    def register_crud_routes(app: FastAPI, base: Base, db: SessionLocal):
                        for cls in base._decl_class_registry.values():
                            if hasattr(cls, '__tablename__'):
                                crud = CRUDBase(cls)
                                model_schema = create_model_schema(cls)

                                @app.get(f"/{cls.__tablename__}/{{id}}")
                                def read(id: int, db: Session = Depends(get_db)):
                                    return crud.get(db, id)

                                @app.post(f"/{cls.__tablename__}/", response_model=model_schema)
                                def create(obj_in: model_schema, db: Session = Depends(get_db)):
                                    return crud.create(db, obj_in.dict())

                                @app.put(f"/{cls.__tablename__}/{{id}}", response_model=model_schema)
                                def update(id: int, obj_in: model_schema, db: Session = Depends(get_db)):
                                    return crud.update(db, id, obj_in.dict())

                                @app.delete(f"/{cls.__tablename__}/{{id}}")
                                def delete(id: int, db: Session = Depends(get_db)):
                                    crud.delete(db, id)
                                    return {"message": "Item deleted successfully."}

                    # Utilize esta função para registrar as rotas automaticamente
                    register_crud_routes(app, Base, SessionLocal)                            