from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from funcoes import db

class Os_imagem(db.Model):
    __tablename__ = 'os_imagem'
    codigo = Column(INTEGER, primary_key=True)
    item = Column(INTEGER)
    caminho = Column(VARCHAR)
    fk_os_master = Column(INTEGER)
