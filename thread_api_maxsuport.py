from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,INTEGER,FLOAT,BOOLEAN,DATETIME, func
import os
import json
from funcoes import parametros, importlib, db,api,app
import datetime
from decimal import Decimal

models_path = os.path.join(os.path.dirname(__file__), 'model')
models = {}

# Carregar todos os arquivos Python na pasta de modelos e importá-los como módulos
for filename in os.listdir(models_path):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        file_path = os.path.join(models_path, filename)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if str(type(attr))=="<class 'flask_sqlalchemy.model.DefaultMeta'>":
                models[attr_name] = attr            
            # if isinstance(attr, db.Model):
            #     models[attr_name] = attr

# Função para converter modelos SQLAlchemy em dicionários
def model_to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        if isinstance(value, Decimal):
            result[c.name] = float(value)
        elif isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
            result[c.name] = value.isoformat()
        elif isinstance(value, str):
            result[c.name] = value.encode('iso-8859-1').decode('iso-8859-1')
        else:
            result[c.name] = value
    return result

def create_model_request(model_cls):
    # Cria um dicionário de campos baseado na estrutura do modelo SQLAlchemy
    model_fields = {}
    for column in model_cls.__table__.columns:
        field_type = fields.String  # Tipo padrão
        example = None  # Exemplo padrão, ajustável conforme o tipo de campo

        if column.primary_key:
            continue  # Pular o campo id se exclude_id estiver ativado para requisições POST, PUT
        
        if isinstance(column.type, INTEGER):
            field_type = fields.Integer
            example = 1
        elif isinstance(column.type, FLOAT):
            field_type = fields.Float
            example = 1.0
        elif isinstance(column.type, BOOLEAN):
            field_type = fields.Boolean
            example = True
        elif isinstance(column.type, DATETIME):
            field_type = fields.DateTime
            example = '2023-01-01T00:00:00'
        
        # Adicionando o campo ao dicionário de modelo com exemplo
        model_fields[column.name] = field_type(description=column.name, example=example, required=column.nullable == False)
    
    # Retornar o modelo criado
    return api.model(model_cls.__name__ + 'Model', model_fields)    


def create_resource_for_model(model_cls):

    model_req = create_model_request(model_cls)
    ns = Namespace(model_cls.__name__.lower(), description=f'Tabela {model_cls.__name__}')
    
    def numerador(db, model_cls, field_name, filter_active=False, where_field=None, where_value=None):
        query = db.session.query(func.max(getattr(model_cls, field_name)).label('MAIOR'))
        if filter_active:
            query = query.filter(getattr(model_cls, where_field) == where_value)
        
        max_value = query.scalar()
        resultado = (max_value + 1) if max_value is not None else 0
        return resultado


    @ns.route('/')
    class DynamicPostListResource(Resource):
        @ns.doc('retorna_todos_registros')
        def get(self):
            items = model_cls.query.limit(25).all()
            return [model_to_dict(item) for item in items], 200

        @ns.doc('cria_registro')
        @ns.expect(model_req)  # Usar o modelo dinâmico
        def post(self):
            data = request.get_json()
            next_id = numerador(db, model_cls, 'codigo')  # Obter o próximo ID
            data['codigo'] = next_id
            item = model_cls(**data)
            db.session.add(item)
            db.session.commit()
            return model_to_dict(item), 201    

    @ns.route('/<int:id>')
    class DynamicResource(Resource):               
        @ns.doc('get_item')
        def get(self, id):
            item = model_cls.query.get(id)
            if item:
                return model_to_dict(item), 200
            return {'message': 'Item not found'}, 404

        @ns.doc('update_item')
        @ns.expect(model_req)  # Reutilizar o mesmo modelo para PUT
        def put(self, id):
            item = model_cls.query.get(id)
            if item:
                data = request.get_json()
                for key, value in data.items():
                    setattr(item, key, value)
                db.session.commit()
                return model_to_dict(item), 200
            return {'message': 'Item not found'}, 404

        @ns.doc('delete_item')
        def delete(self, id):
            item = model_cls.query.get(id)
            if item:
                db.session.delete(item)
                db.session.commit()
                return {'message': 'Item deleted'}, 204
            return {'message': 'Item not found'}, 404
        
   

    return ns

# Criar rotas da API para cada modelo carregado
for model_name, model_cls in models.items():
    ns = create_resource_for_model(model_cls)
    api.add_namespace(ns, path=f'/{model_name.lower()}')

if __name__ == '__main__':
    app.run(debug=True,host='192.168.10.207', port=5000)