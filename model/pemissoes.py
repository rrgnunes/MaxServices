from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pemissoes(Base):
    __tablename__ = 'pemissoes'
    fkusuario = Column(INTEGER, primary_key=True)
    fktela = Column(INTEGER, primary_key=True)
    visualizar = Column(VARCHAR)
    excluir = Column(VARCHAR)
    editar = Column(VARCHAR)
    incluir = Column(VARCHAR)
    visivel = Column(VARCHAR)
