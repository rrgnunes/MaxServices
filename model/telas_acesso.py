from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Telas_acesso(Base):
    __tablename__ = 'telas_acesso'
    codigo = Column(INTEGER, primary_key=True)
    fk_usuario = Column(INTEGER)
    fk_tela = Column(INTEGER)
    visualiza = Column(VARCHAR)
    inseri = Column(VARCHAR)
    altera = Column(VARCHAR)
    exclui = Column(VARCHAR)
