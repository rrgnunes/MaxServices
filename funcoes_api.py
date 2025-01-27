from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DB:
    def __init__(self, engine):
        self.engine = engine
        self.session = None

    def init_session(self):
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

db = DB(None)  # Inicialização do objeto global
