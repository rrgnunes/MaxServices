from sqlalchemy import Column, INTEGER, DOUBLE, CHAR,TIMESTAMP, VARCHAR, BLOB, NUMERIC, SMALLINT, DATE, DECIMAL, BIGINT, TIME  # Adicione mais tipos conforme necessário
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Beneficio_fiscal(Base):
    __tablename__ = 'beneficio_fiscal'
    codigo = Column(INTEGER, primary_key=True)
    abreviatura = Column(VARCHAR)
    descricao = Column(VARCHAR)
    cst00 = Column(VARCHAR)
    cst10 = Column(VARCHAR)
    cst20 = Column(VARCHAR)
    cst30 = Column(VARCHAR)
    cst40 = Column(VARCHAR)
    cst41 = Column(VARCHAR)
    cst50 = Column(VARCHAR)
    cst51 = Column(VARCHAR)
    cst60 = Column(VARCHAR)
    cst70 = Column(VARCHAR)
    cst90 = Column(VARCHAR)
