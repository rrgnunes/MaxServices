from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    codigo = Column(SMALLINT, primary_key=True)
    login = Column(VARCHAR)
    senha = Column(VARCHAR)
    hierarquia = Column(SMALLINT)
    ecaixa = Column(VARCHAR)
    supervisor = Column(VARCHAR)
    ativo = Column(VARCHAR)
    ultimo_pedido = Column(INTEGER)
    ultima_venda = Column(INTEGER)
    senha_app = Column(VARCHAR)
    app_senha = Column(VARCHAR)
    fk_vendedor = Column(INTEGER)
    fk_empresa = Column(INTEGER)
